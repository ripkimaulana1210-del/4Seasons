#version 330 core

uniform sampler2D u_texture;
uniform vec3 u_tint;
uniform float u_alpha;

in vec2 uv;

out vec4 fragColor;

void main() {
    vec4 texel = texture(u_texture, uv);
    fragColor = vec4(texel.rgb * u_tint, texel.a * u_alpha);
}
