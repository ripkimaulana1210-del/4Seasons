#version 330 core

layout (location = 0) in vec3 in_normal;
layout (location = 1) in vec3 in_position;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

void main() {
    vec3 position = in_position + in_normal * 0.000001;
    gl_Position = m_proj * m_view * m_model * vec4(position, 1.0);
}
