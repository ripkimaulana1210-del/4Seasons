#version 330 core

layout (location = 0) in vec3 in_normal;
layout (location = 1) in vec3 in_position;
layout (location = 2) in vec2 in_uv;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;
uniform vec2 u_repeat;

out vec3 frag_pos;
out vec3 normal;
out vec2 uv;

void main() {
    vec4 world_pos = m_model * vec4(in_position, 1.0);
    frag_pos = world_pos.xyz;
    normal = mat3(transpose(inverse(m_model))) * in_normal;
    uv = in_uv * u_repeat;
    gl_Position = m_proj * m_view * world_pos;
}
