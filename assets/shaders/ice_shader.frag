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

in vec3 v_world_pos;
in vec3 v_normal;
in vec2 v_uv;
in float v_crystal;

out vec4 fragColor;

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

    vec3 lit = light.Ia * base * 1.20 + light.Id * diff * base * 0.82 + light.Is * spec * 0.25;
    fragColor = vec4(lit, 0.82);
}
