SAMPLING_RATE = 8000  # Defined in test task
USE_ONNX = False  # TODO check
import asyncio
import io
import torch
import torchaudio


class VoiceDetect:
    def __init__(
        self,
        sampling_rate: int = SAMPLING_RATE,
        num_threads: int = 4,
        use_onnx: bool = USE_ONNX,
    ):
        self.sampling_rate = sampling_rate
        self.num_threads = num_threads
        self.use_onnx = use_onnx
        torch.set_num_threads(self.num_threads)
        self.model, self.utils = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=True,
            onnx=self.use_onnx,
        )
        (
            self.get_speech_timestamps,
            self.save_audio,
            self.read_audio,
            self.VADIterator,
            self.collect_chunks,
        ) = self.utils

    @staticmethod
    def bytes_to_wav(data: bytes, sampling_rate: int = SAMPLING_RATE) -> torch.Tensor:
        wav, sr = torchaudio.load(io.BytesIO(data))
        if wav.size(0) > 1:
            wav = wav.mean(dim=0, keepdim=True)

        if sr != sampling_rate:
            transform = torchaudio.transforms.Resample(
                orig_freq=sr, new_freq=sampling_rate
            )
            wav = transform(wav)
            sr = sampling_rate

        assert sr == sampling_rate
        return wav.squeeze(0)

    async def voice_prob(self, binary: bytes, sampling_rate: int = SAMPLING_RATE, attempt: int = 0):
        try:
            wav = self.bytes_to_wav(binary, sampling_rate)
            print(f"wav readed. len={len(wav)}")
            prob = self.model(wav, sampling_rate).item()
            print(f"prob={prob}")
            if attempt > 0:
                print (f"attempt {attempt} success")
            return prob
        except Exception as e:
            print (f"Voice attempt {attempt} failed")
            if attempt > 2:
                return None
            else:
                print(e)
            await asyncio.sleep(1 / 1000)
            print (f"retrying...")
            return await self.voice_prob(binary, sampling_rate, attempt+1)
