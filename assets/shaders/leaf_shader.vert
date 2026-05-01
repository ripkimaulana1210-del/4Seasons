#version 330

layout (location = 0) in vec3 in_normal;
layout (location = 1) in vec3 in_position;
layout (location = 2) in vec2 in_uv;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;
uniform float u_time;

out vec3 v_normal;
out vec3 v_frag_pos;
out vec2 v_uv;

void main() {
    vec3 pos = in_position;

    // daun di bagian atas pohon bergerak sedikit
    float sway_mask = smoothstep(1.4, 4.8, pos.y);
    float phase = u_time * 1.9 + pos.x * 6.0 + pos.z * 5.0;

    pos.x += sin(phase) * 0.03 * sway_mask;
    pos.z += cos(phase * 0.85) * 0.02 * sway_mask;

    vec4 world_pos = m_model * vec4(pos, 1.0);

    mat3 normal_matrix = mat3(transpose(inverse(m_model)));
    v_normal = normalize(normal_matrix * in_normal);
    v_frag_pos = world_pos.xyz;
    v_uv = in_uv;

    gl_Position = m_proj * m_view * world_pos;
}