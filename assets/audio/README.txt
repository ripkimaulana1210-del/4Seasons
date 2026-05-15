Seasonal audio folder.

Active music files:
- spring_sparkle.mp3: Spring / early spring / hanami / tsuyu.
- summer_silhouette.mp3: Summer / midsummer / late summer.
- autumn_unravel.mp3: Autumn / momiji.
- winter_call_of_silence_cut.wav: First frost / winter / deep winter.

Current behavior:
- The game selects music by season group in engine/systems/audio_manager.py.
- Procedural ambience is disabled because it sounded distracting.
- Transition cue sounds are still generated in code.

Current notes:
- Pygame usually supports .mp3, .ogg, and .wav, depending on SDL_mixer.
- winter_call_of_silence_cut.wav is the trimmed/compatible version used by Pygame.
