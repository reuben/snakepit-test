import argparse
import boto3
import os
import pandas
import tempfile
import unicodedata
import urllib

from multiprocessing.dummy import Pool
from sox import Transformer
from boto3.s3.transfer import TransferConfig


TRANSFER_CONFIG = TransferConfig(use_threads=False)

parser = argparse.ArgumentParser()
parser.add_argument('--csv', required=True)
parser.add_argument('--dest_folder', required=True)
parser.add_argument('--tmp_folder', required=True)
parser.add_argument('--normalize_english_transcripts', action='store_true')
args = parser.parse_args()


def validate_label(label):
    label = urllib.parse.unquote(label)

    label = label.replace("-", "")
    label = label.replace("_", "")
    label = label.replace(".", "")
    label = label.replace(",", "")
    label = label.replace("?", "")
    label = label.strip()

    return label.lower()


def process_one_clip(clip):
    _, clip = clip # index, Series = clip

    if clip['up_votes'] > clip['down_votes']:
        validation = 'valid'
    else:
        validation = 'invalid'

    path = clip['path'].replace('/', '___')
    mp3_dest_path = os.path.join(args.tmp_folder, clip['locale'], path)
    wav_dest_path = os.path.join(args.dest_folder, clip['locale'], validation, path[:-3] + 'wav')

    if not os.path.exists(mp3_dest_path):
        bucket.download_file(clip['path'], mp3_dest_path, Config=TRANSFER_CONFIG)

    if not os.path.exists(wav_dest_path):
        transformer = Transformer()
        transformer.convert(samplerate=16000, n_channels=1, bitdepth=16)
        transformer.build(mp3_dest_path, wav_dest_path)

    transcript = clip['sentence']
    if clip['locale'] == 'en' and args.normalize_english_transcripts:
        transcript = (unicodedata.normalize('NFKD', transcript)
                                 .encode('ascii', 'ignore')
                                 .decode('ascii', 'ignore'))
        transcript = validate_label(transcript)

    return (clip['locale'], validation, os.path.abspath(wav_dest_path), os.path.getsize(wav_dest_path), transcript)


if __name__ == '__main__':
    if not os.path.exists(args.tmp_folder):
        os.makedirs(args.tmp_folder)

    bucket = boto3.resource('s3').Bucket('voice-prod-clips-393eefd0cba28c270ced0f9587a4f6ae601ca91e')

    clips = pandas.read_csv(args.csv, sep=None, encoding='utf-8')

    locales = clips['locale'].unique()
    print('found {} locales, creating folders...'.format(len(locales)))

    for locale in locales:
        print('mkdir', os.path.join(args.dest_folder, locale))
        print('mkdir', os.path.join(args.tmp_folder, locale))
        os.makedirs(os.path.join(args.tmp_folder, locale), exist_ok=True)
        os.makedirs(os.path.join(args.dest_folder, locale, 'valid'), exist_ok=True)
        os.makedirs(os.path.join(args.dest_folder, locale, 'invalid'), exist_ok=True)

    pool = Pool()
    results = pool.map(process_one_clip, clips.iterrows())
    pool.close()
    pool.join()

    data = pandas.DataFrame(data=results, columns=('locale', 'validation', 'wav_filename', 'wav_filesize', 'transcript'))

    for locale in locales:
        locale_data = data[data['locale'] == locale]
        valid = locale_data[locale_data['validation'] == 'valid'].ix[:, ('wav_filename', 'wav_filesize', 'transcript')]
        invalid = locale_data[locale_data['validation'] == 'invalid'].ix[:, ('wav_filename', 'wav_filesize', 'transcript')]
        valid.to_csv(os.path.join(args.dest_folder, locale, 'cv_{}_valid.csv'.format(locale)), index=False)
        invalid.to_csv(os.path.join(args.dest_folder, locale, 'cv_{}_invalid.csv'.format(locale)), index=False)
