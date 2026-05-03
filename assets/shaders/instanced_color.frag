#version 330 core

struct Light {
    vec3 position;
    vec3 Ia;
    vec3 Id;
    vec3 Is;
};

uniform Light light;
uniform vec3 cam_pos;
uniform vec3 u_fog_color;
uniform float u_fog_density;
uniform float u_fog_start;
uniform float u_fog_end;
uniform sampler2D u_shadow_map;
uniform float u_shadow_strength;

in vec3 frag_pos;
in vec3 normal;
in vec3 instance_color;
in vec4 shadow_pos;

out vec4 fragColor;

vec3 apply_fog(vec3 color, vec3 world_pos) {
    float distance_to_camera = length(cam_pos - world_pos);
    float range_fog = smoothstep(u_fog_start, u_fog_end, distance_to_camera);
    float air_fog = 1.0 - exp(-distance_to_camera * u_fog_density * 0.030);
    float fog_amount = clamp(max(range_fog * u_fog_density, air_fog), 0.0, 0.82);
    return mix(color, u_fog_color, fog_amount);
}

float shadow_factor(vec3 N, vec3 L) {
    vec3 proj = shadow_pos.xyz / shadow_pos.w;
    proj = proj * 0.5 + 0.5;
    if (proj.z > 1.0 || proj.x < 0.0 || proj.x > 1.0 || proj.y < 0.0 || proj.y > 1.0) {
        return 1.0;
    }

    float bias = max(0.0028 * (1.0 - dot(N, L)), 0.0009);
    vec2 texel = 1.0 / vec2(textureSize(u_shadow_map, 0));
    float shadow = 0.0;
    for (int x = -1; x <= 1; x++) {
        for (int y = -1; y <= 1; y++) {
            float closest = texture(u_shadow_map, proj.xy + vec2(x, y) * texel).r;
            shadow += proj.z - bias > closest ? 1.0 : 0.0;
        }
    }
    shadow /= 9.0;
    return mix(1.0, 1.0 - u_shadow_strength, shadow);
}

void main() {
    vec3 N = normalize(normal);
    vec3 L = normalize(light.position - frag_pos);
    vec3 V = normalize(cam_pos - frag_pos);
    if (dot(N, V) < 0.0) {
        N = -N;
    }
    vec3 R = reflect(-L, N);

    float diff = max(dot(N, L), 0.0);
    float spec = pow(max(dot(V, R), 0.0), 32.0) * step(0.0, diff);

    vec3 ambient = light.Ia * instance_color;
    vec3 diffuse = light.Id * diff * instance_color;
    vec3 specular = light.Is * spec;
    float shadow = shadow_factor(N, L);
    vec3 final_color = ambient + (diffuse + specular) * shadow;

    fragColor = vec4(apply_fog(final_color, frag_pos), 1.0);
}
