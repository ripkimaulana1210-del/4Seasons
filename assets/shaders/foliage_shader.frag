#version 330 core

struct Light {
    vec3 position;
    vec3 Ia;
    vec3 Id;
    vec3 Is;
};

uniform Light light;
uniform vec3 cam_pos;
uniform vec3 u_color;
uniform float u_time;
uniform float u_night_factor;
uniform vec3 u_fog_color;
uniform float u_fog_density;
uniform float u_fog_start;
uniform float u_fog_end;
uniform sampler2D u_shadow_map;
uniform float u_shadow_strength;

in vec3 frag_pos;
in vec3 normal;
in float sway_mix;
in float height_mix;
in vec4 shadow_pos;

out vec4 fragColor;

vec3 apply_fog(vec3 color, vec3 world_pos) {
    float distance_to_camera = length(cam_pos - world_pos);
    float range_fog = smoothstep(u_fog_start, u_fog_end, distance_to_camera);
    float air_fog = 1.0 - exp(-distance_to_camera * u_fog_density * 0.030);
    float fog_amount = clamp(max(range_fog * u_fog_density, air_fog), 0.0, 0.78);
    return mix(color, u_fog_color, fog_amount);
}

float shadow_factor(vec3 N, vec3 L) {
    vec3 proj = shadow_pos.xyz / shadow_pos.w;
    proj = proj * 0.5 + 0.5;
    if (proj.z > 1.0 || proj.x < 0.0 || proj.x > 1.0 || proj.y < 0.0 || proj.y > 1.0) {
        return 1.0;
    }

    float bias = max(0.0036 * (1.0 - dot(N, L)), 0.0012);
    vec2 texel = 1.0 / vec2(textureSize(u_shadow_map, 0));
    float shadow = 0.0;
    for (int x = -1; x <= 1; x++) {
        for (int y = -1; y <= 1; y++) {
            float closest = texture(u_shadow_map, proj.xy + vec2(x, y) * texel).r;
            shadow += proj.z - bias > closest ? 1.0 : 0.0;
        }
    }
    shadow /= 9.0;
    return mix(1.0, 1.0 - u_shadow_strength * 0.72, shadow);
}

void main() {
    vec3 N = normalize(normal);
    vec3 L = normalize(light.position - frag_pos);
    vec3 V = normalize(cam_pos - frag_pos);
    if (dot(N, V) < 0.0) {
        N = -N;
    }
    vec3 H = normalize(L + V);

    float diff = max(dot(N, L), 0.0);
    float rim = pow(1.0 - max(dot(N, V), 0.0), 2.2);
    float spec = pow(max(dot(N, H), 0.0), 24.0) * 0.10;
    float life = 0.94 + 0.08 * sin(u_time * 0.9 + sway_mix * 2.4 + height_mix * 3.1);

    vec3 base = u_color * life;
    vec3 underside = u_color * 0.62;
    base = mix(underside, base, 0.55 + 0.45 * diff);

    vec3 night_tint = vec3(0.34, 0.42, 0.62);
    base = mix(base, base * night_tint, u_night_factor * 0.55);

    vec3 ambient = light.Ia * base * 1.15;
    vec3 diffuse = light.Id * diff * base;
    vec3 rim_light = mix(vec3(1.0, 0.70, 0.92), vec3(0.54, 0.70, 1.0), u_night_factor) * rim * 0.20;
    vec3 specular = light.Is * spec;
    float shadow = shadow_factor(N, L);

    fragColor = vec4(apply_fog(ambient + (diffuse + rim_light + specular) * shadow, frag_pos), 1.0);
}
