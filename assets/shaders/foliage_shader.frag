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

in vec3 frag_pos;
in vec3 normal;
in float sway_mix;
in float height_mix;

out vec4 fragColor;

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

    fragColor = vec4(ambient + diffuse + rim_light + specular, 1.0);
}
