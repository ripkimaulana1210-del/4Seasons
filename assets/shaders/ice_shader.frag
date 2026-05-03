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

in vec3 v_world_pos;
in vec3 v_normal;
in vec2 v_uv;
in float v_crystal;
in vec4 v_shadow_pos;

out vec4 fragColor;

vec3 apply_fog(vec3 color, vec3 world_pos) {
    float distance_to_camera = length(cam_pos - world_pos);
    float range_fog = smoothstep(u_fog_start, u_fog_end, distance_to_camera);
    float air_fog = 1.0 - exp(-distance_to_camera * u_fog_density * 0.030);
    float fog_amount = clamp(max(range_fog * u_fog_density, air_fog), 0.0, 0.74);
    return mix(color, u_fog_color, fog_amount);
}

float shadow_factor(vec3 N, vec3 L) {
    vec3 proj = v_shadow_pos.xyz / v_shadow_pos.w;
    proj = proj * 0.5 + 0.5;
    if (proj.z > 1.0 || proj.x < 0.0 || proj.x > 1.0 || proj.y < 0.0 || proj.y > 1.0) {
        return 1.0;
    }
    float bias = max(0.0030 * (1.0 - dot(N, L)), 0.0010);
    float closest = texture(u_shadow_map, proj.xy).r;
    float shadow = proj.z - bias > closest ? 1.0 : 0.0;
    return mix(1.0, 1.0 - u_shadow_strength * 0.42, shadow);
}

float crack_line(float value, float width) {
    return 1.0 - smoothstep(0.0, width, abs(fract(value) - 0.5));
}

void main() {
    vec3 N = normalize(v_normal);
    vec3 L = normalize(light.position - v_world_pos);
    vec3 V = normalize(cam_pos - v_world_pos);
    vec3 H = normalize(L + V);

    float diff = max(dot(N, L), 0.0);
    float spec = pow(max(dot(N, H), 0.0), 96.0);
    float fresnel = pow(1.0 - max(dot(N, V), 0.0), 2.4);

    float crack_a = crack_line(v_uv.x * 9.0 + v_uv.y * 2.0 + v_crystal * 0.3, 0.045);
    float crack_b = crack_line(v_uv.y * 11.0 - v_uv.x * 1.5, 0.030);
    float cracks = max(crack_a * 0.55, crack_b * 0.40);
    float shimmer = 0.5 + 0.5 * sin(u_time * 1.4 + v_world_pos.x * 1.7 + v_world_pos.z * 1.2);

    vec3 deep = mix(vec3(0.36, 0.62, 0.74), vec3(0.12, 0.22, 0.36), u_night_factor);
    vec3 pale = mix(u_color, vec3(0.56, 0.72, 1.0), u_night_factor * 0.45);
    vec3 base = mix(deep, pale, 0.58 + v_crystal * 0.12);
    base += cracks * vec3(0.34, 0.52, 0.62);
    base += fresnel * vec3(0.46, 0.72, 1.0) * (0.32 + u_night_factor * 0.28);
    base += spec * vec3(1.0) * (0.35 + shimmer * 0.25);

    float shadow = shadow_factor(N, L);
    vec3 lit = light.Ia * base * 1.20 + (light.Id * diff * base * 0.82 + light.Is * spec * 0.25) * shadow;
    fragColor = vec4(apply_fog(lit, v_world_pos), 0.82);
}
