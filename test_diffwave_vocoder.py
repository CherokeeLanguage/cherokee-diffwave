import datetime
import glob
import random
import shutil

import progressbar
from progressbar import ProgressBar
from pydub import AudioSegment
from torch import Tensor

import numpy
import os
import sys
import torch
import torchaudio
from typing import List
from typing import Tuple

from diffwave.inference import predict as diffwave_predict


def cd_script_dir() -> None:
    if sys.argv[0].strip():
        dir_name: str = os.path.dirname(sys.argv[0])
        if dir_name:
            os.chdir(dir_name)


def main():
    mp3_set_title: str = "diffwave test"
    mp3_copyright_by: str = "Michael Conrad"
    mp3_encoded_by: str = "Michael Conrad"
    mp3_copy_year: str = str(datetime.date.today().year)

    weights_dir: str = os.path.expanduser("~/git/cherokee-diffwave/models/")
    cd_script_dir()
    model_pt = os.path.join(weights_dir, "weights.pt")
    npy_files: List[str] = list()
    npy_files.extend(sorted(glob.glob("wavs/??????/*.wav.spec.npy")))
    ran = random.Random(0)
    npy_files = ran.sample(npy_files, 100)
    bar: ProgressBar = progressbar.ProgressBar(maxval=len(npy_files))
    bar.start()
    npy_wav_files: List[Tuple[str, str, str]] = list()
    shutil.rmtree("tmp", ignore_errors=True)
    os.mkdir("tmp")
    for npy_file in npy_files:
        npy_name = os.path.basename(npy_file)
        wav_file = os.path.join("tmp", f"{os.path.splitext(npy_name)[0]}.wav")
        mp3_file = os.path.join("tmp", f"{os.path.splitext(npy_name)[0]}.mp3")
        npy_wav_files.append((npy_file, wav_file, mp3_file))
    ix: int = 0
    for npy_file, wav_file, mp3_file in npy_wav_files:
        nd_array = numpy.load(npy_file)
        spectrogram: Tensor = torch.from_numpy(nd_array).float()
        # spectrogram = torch.clamp((spectrogram + 100) / 100, 0.0, 1.0)
        audio, sr = diffwave_predict(spectrogram, model_pt, device=torch.device("cuda"))
        torchaudio.save(wav_file, audio.cpu(), sample_rate=sr)
        mp3_data: AudioSegment = AudioSegment.from_file(wav_file)
        os.remove(wav_file)

        id3v2_tags: dict = dict()
        id3v2_tags["COMM"] = "diffwave weights test"
        id3v2_tags["TALB"] = "diffwave weights test"
        id3v2_tags["TCON"] = "Speech"
        id3v2_tags["TCOP"] = "CC BY-SA"
        id3v2_tags["TDRC"] = mp3_copy_year
        id3v2_tags["TENC"] = mp3_encoded_by
        id3v2_tags["TOWN"] = mp3_copyright_by
        id3v2_tags["TRCK"] = f"{ix + 1}/{len(npy_files)}"
        ix += 1

        mp3_data.export(mp3_file, format="mp3", parameters=["-qscale:a", "3"])
        bar.update(bar.currval+1)
    bar.finish()


if __name__ == "__main__":
    main()
