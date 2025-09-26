import sys
import os

def speak(text: str) -> None:
    """
    Speak a line of text aloud.

    Priority:
      1. Use `yapper-tts` if installed.
      2. Otherwise fall back to OS native tools:
         - macOS: `say`
         - Linux: `espeak`
         - Windows: PowerShell Speech Synthesizer
    """

    # Try using yapper-tts
    try:
        from yapper import Yapper, PiperSpeaker, PiperVoiceUS, GeminiEnhancer
        # Use plain mode so no enhancement (unless you want personality / enhancer)
        Squib = PiperSpeaker(
            voice=PiperVoiceUS.HFC_MALE
        )
        y = Yapper(speaker=Squib,
                   enhancer=GeminiEnhancer(api_key='YOUR KEY HERE'))
        y.yap(text)
        return
    except ImportError:
        # Not installed
        pass
    except Exception as e:
        # Something went wrong in yapper, fallback
        print(f"[WARN] yapper failed: {e}")

    # Fallbacks
    # Escaping text where needed
    safe_text = text.replace('"', '\\"')

    if sys.platform == "darwin":
        os.system(f'say "{safe_text}"')

    elif sys.platform.startswith("linux"):
        # Check if espeak exists?
        # Optionally test with which:
        if _which("espeak"):
            os.system(f'espeak "{safe_text}"')
        else:
            print("[ERROR] espeak not found; cannot speak text on Linux fallback.")

    elif sys.platform.startswith("win"):
        # Fix: Proper quotes for PowerShell
        escaped = text.replace('"', '`"')
        ps_command = (
            'powershell -Command '
            "Add-Type -AssemblyName System.Speech; "
            f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\\"{escaped}\\")'
        )
        os.system(ps_command)

    else:
        print(f"[ERROR] No TTS fallback for platform {sys.platform}.")


def _which(cmd: str) -> bool:
    """
    Simple version of UNIX which: check if `cmd` is available in PATH.
    """
    for path in os.environ.get("PATH", "").split(os.pathsep):
        full = os.path.join(path, cmd)
        if os.path.isfile(full) and os.access(full, os.X_OK):
            return True
    return False


if __name__ == "__main__":
    speak("Hello, this is using yapper-tts or fallback TTS.")