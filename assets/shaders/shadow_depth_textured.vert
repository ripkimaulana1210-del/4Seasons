#version 330 core

layout (location = 0) in vec3 in_normal;
layout (location = 1) in vec3 in_position;
layout (location = 2) in vec2 in_uv;

uniform mat4 m_model;
uniform mat4 m_light_space;

void main() {
    vec3 pos = in_position + in_normal * 0.000001 + vec3(in_uv, 0.0) * 0.000001;
    gl_Position = m_light_space * m_model * vec4(pos, 1.0);
}
