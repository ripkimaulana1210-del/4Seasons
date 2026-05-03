#version 330 core

uniform sampler2D u_texture;

in vec2 uv;

out vec4 fragColor;

void main() {
    fragColor = texture(u_texture, uv);
}
