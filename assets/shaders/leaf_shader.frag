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

in vec3 v_normal;
in vec3 v_frag_pos;
in vec2 v_uv;

out vec4 fragColor;

float leaf_mask(vec2 uv) {
    // uv: 0..1
    float x = abs(uv.x * 2.0 - 1.0);
    float y = clamp(uv.y, 0.0, 1.0);

    // bentuk daun: runcing di bawah/atas, lebar di tengah
    float half_width = 0.05 + sin(y * 3.14159265) * 0.52;

    return step(x, half_width);
}

void main() {
    float mask = leaf_mask(v_uv);
    if (mask < 0.5) {
        discard;
    }

    vec3 N = normalize(v_normal);
    vec3 L = normalize(light.position - v_frag_pos);
    vec3 V = normalize(cam_pos - v_frag_pos);
    vec3 R = reflect(-L, N);

    float diff = max(dot(N, L), 0.0);
    float spec = pow(max(dot(V, R), 0.0), 18.0) * 0.15;

    // warna dasar daun
    vec3 base = mix(u_color * 0.82, u_color * 1.10, v_uv.y);

    // garis tengah daun
    float center_vein = 1.0 - smoothstep(0.0, 0.08, abs(v_uv.x - 0.5));
    base += center_vein * vec3(0.08, 0.12, 0.04);

    // tepi sedikit lebih gelap
    float edge_dark = smoothstep(0.0, 0.48, abs(v_uv.x - 0.5));
    base -= edge_dark * vec3(0.03, 0.05, 0.02);

    vec3 ambient = light.Ia * base;
    vec3 diffuse = light.Id * diff * base;
    vec3 specular = light.Is * spec;

    fragColor = vec4(ambient + diffuse + specular, 1.0);
}