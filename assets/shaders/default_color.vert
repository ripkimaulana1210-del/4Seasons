#version 330 core

layout (location = 0) in vec3 in_normal;
layout (location = 1) in vec3 in_position;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;
uniform mat4 m_light_space;

out vec3 frag_pos;
out vec3 normal;
out vec4 shadow_pos;

void main() {
    vec4 world_pos = m_model * vec4(in_position, 1.0);
    frag_pos = world_pos.xyz;
    normal = mat3(transpose(inverse(m_model))) * in_normal;
    shadow_pos = m_light_space * world_pos;
    gl_Position = m_proj * m_view * world_pos;
}
