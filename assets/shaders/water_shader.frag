#version 330

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

in vec3 v_world_pos;
in vec3 v_normal;
in float v_wave;
in vec2 v_uv;

out vec4 fragColor;

void main() {
    vec3 N = normalize(v_normal);
    vec3 L = normalize(light.position - v_world_pos);
    vec3 V = normalize(cam_pos - v_world_pos);
    vec3 H = normalize(L + V);

    float diff = max(dot(N, L), 0.0);

    float spec = pow(max(dot(N, H), 0.0), 96.0);
    spec *= 0.75;

    float fresnel = pow(1.0 - max(dot(N, V), 0.0), 2.8);

    vec3 deep_color = vec3(0.03, 0.15, 0.24);
    vec3 shallow_color = vec3(0.12, 0.34, 0.50);
    vec3 sky_reflect = vec3(0.52, 0.68, 0.86);

    float uv_ripple = sin((v_uv.x * 18.0 + v_uv.y * 21.0) + u_time * 0.9) * 0.035;
    float ripple_mask = 0.5 + v_wave * 8.0 + uv_ripple;
    ripple_mask = clamp(ripple_mask, 0.0, 1.0);

    vec3 base = mix(deep_color, shallow_color, ripple_mask);
    base = mix(base, u_color, 0.25);

    vec3 ambient = light.Ia * base * 1.2;
    vec3 diffuse = light.Id * diff * base * 0.9;
    vec3 reflection = sky_reflect * fresnel * 0.38;
    vec3 specular = light.Is * spec * vec3(1.0);

    vec3 final_color = ambient + diffuse + reflection + specular;

    fragColor = vec4(final_color, 0.96);
}
