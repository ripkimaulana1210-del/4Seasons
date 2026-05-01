#version 330 core

struct Light {
    vec3 position;
    vec3 Ia;
    vec3 Id;
    vec3 Is;
};

uniform Light light;
uniform sampler2D u_texture;
uniform vec3 cam_pos;
uniform vec3 u_tint;
uniform float u_alpha;

in vec3 frag_pos;
in vec3 normal;
in vec2 uv;

out vec4 fragColor;

void main() {
    vec4 texel = texture(u_texture, uv);
    vec3 base_color = texel.rgb * u_tint;

    vec3 N = normalize(normal);
    vec3 L = normalize(light.position - frag_pos);
    vec3 V = normalize(cam_pos - frag_pos);
    if (dot(N, V) < 0.0) {
        N = -N;
    }
    vec3 R = reflect(-L, N);

    float diff = max(dot(N, L), 0.0);
    float spec = pow(max(dot(V, R), 0.0), 24.0) * step(0.0, diff) * 0.35;

    vec3 ambient = light.Ia * base_color;
    vec3 diffuse = light.Id * diff * base_color;
    vec3 specular = light.Is * spec;

    fragColor = vec4(ambient + diffuse + specular, texel.a * u_alpha);
}
