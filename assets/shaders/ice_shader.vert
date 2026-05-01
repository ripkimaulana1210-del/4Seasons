#version 330 core

in vec3 in_normal;
in vec3 in_position;
in vec2 in_uv;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;
uniform float u_time;

out vec3 v_world_pos;
out vec3 v_normal;
out vec2 v_uv;
out float v_crystal;

void main() {
    vec3 pos = in_position;
    float crystal = sin(pos.x * 8.0 + pos.z * 5.0) * cos(pos.z * 7.0 - pos.x * 3.0);
    pos.y += crystal * 0.006;

    vec4 world_pos = m_model * vec4(pos, 1.0);
    v_world_pos = world_pos.xyz;
    v_normal = normalize(mat3(transpose(inverse(m_model))) * in_normal);
    v_uv = in_uv;
    v_crystal = crystal;

    gl_Position = m_proj * m_view * world_pos;
}
