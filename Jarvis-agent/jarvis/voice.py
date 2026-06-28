"""Voz TTS/STT."""

import asyncio
import os
import tempfile
import threading
from typing import Callable, Optional

import pygame
import speech_recognition as sr
import edge_tts

from . import config


class VoiceEngine:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except Exception:
            pass
        self.speaking = False
        self.interrupted = False
        self.lock = threading.Lock()
        self.current_thread = None

    def speak(self, text, on_complete=None):
        if not text or not text.strip():
            if on_complete: on_complete()
            return
        with self.lock:
            self.interrupted = True
            if self.current_thread and self.current_thread.is_alive():
                try: pygame.mixer.music.stop()
                except: pass
                self.current_thread.join(timeout=0.3)
            self.interrupted = False
            self.current_thread = threading.Thread(
                target=self._speak_thread, args=(text, on_complete), daemon=True
            )
            self.current_thread.start()

    def _speak_thread(self, text, on_complete):
        tmp_path = None
        try:
            with self.lock:
                if self.interrupted: return
                self.speaking = True
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", dir=config.DATA_DIR)
            tmp_path = tmp.name
            tmp.close()

            async def synth():
                tts = edge_tts.Communicate(text, config.TTS_VOICE, rate="-5%", pitch="-3Hz")
                await tts.save(tmp_path)

            try: asyncio.run(synth())
            except Exception: return

            with self.lock:
                if self.interrupted: return

            try:
                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    with self.lock:
                        if self.interrupted:
                            pygame.mixer.music.stop()
                            break
                    pygame.time.Clock().tick(15)
            except Exception: pass
        finally:
            if tmp_path:
                try: os.unlink(tmp_path)
                except: pass
            with self.lock: self.speaking = False
            if on_complete: on_complete()

    def stop(self):
        with self.lock:
            self.interrupted = True
            try: pygame.mixer.music.stop()
            except: pass


class STTEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.microphone = None
        self.stop_fn = None
        self.listening = False
        self.callback = None

    def start(self, callback):
        if self.listening: return
        if not self.microphone:
            self.microphone = sr.Microphone()
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=config.AMBIENT_DURATION)
        self.callback = callback

        def on_audio(recognizer, audio):
            try:
                text = recognizer.recognize_google(audio, language=config.STT_LANGUAGE)
                if self.callback and text: self.callback(text)
            except sr.UnknownValueError: pass
            except Exception: pass

        self.stop_fn = self.recognizer.listen_in_background(
            self.microphone, on_audio, phrase_time_limit=15
        )
        self.listening = True

    def stop(self):
        self.listening = False
        if self.stop_fn:
            self.stop_fn(wait_for_stop=False)
            self.stop_fn = None
