import argparse
import pandas
import os

parser = argparse.ArgumentParser()
parser.add_argument('--source_tsv')
parser.add_argument('--train_dest')
parser.add_argument('--dev_dest')
parser.add_argument('--test_dest')
parser.add_argument('--wavs_dir')
args = parser.parse_args()

df = pandas.read_csv(args.source_tsv, encoding='utf8', sep='\t')
print('Total samples in input file ({}) = {}'.format(args.source_tsv, len(df)))

df['wav_filename'] = df['path'].str.replace(r'(^)', lambda m: os.path.join(args.wavs_dir, m.group(1)))
df['wav_filename'] = df['wav_filename'] + '.wav'
df['wav_filesize'] = df['wav_filename'].apply(lambda x: os.path.getsize(x) if os.path.exists(x) else None)
df['transcript'] = df['sentence'].str.lower()
df = df.loc[:, ['wav_filename', 'wav_filesize', 'transcript']]
df.dropna(inplace=True)
print('Samples after removing non-existent audio files = {}'.format(len(df)))

# One sentence in the dataset contains an email
df = df[~df['transcript'].str.contains('@')]

# These characters are from foreign proper nouns and only appear a handful of times
df = df[~df['transcript'].str.contains('ş')]
df = df[~df['transcript'].str.contains('ă')]
df = df[~df['transcript'].str.contains('ș')]
print('Samples after removing invalid transcripts = {}'.format(len(df)))

# Remove punctuation
df['transcript'] = df['transcript'].str.replace('!', '')
df['transcript'] = df['transcript'].str.replace(r'\(', '')
df['transcript'] = df['transcript'].str.replace(r'\)', '')
df['transcript'] = df['transcript'].str.replace('"', '')
df['transcript'] = df['transcript'].str.replace('“', '')
df['transcript'] = df['transcript'].str.replace('„', '')
df['transcript'] = df['transcript'].str.replace(',', '')
df['transcript'] = df['transcript'].str.replace('.', '')
df['transcript'] = df['transcript'].str.replace("'", '')
df['transcript'] = df['transcript'].str.replace("/", '')
df['transcript'] = df['transcript'].str.replace(":", '')
df['transcript'] = df['transcript'].str.replace("?", '')
df['transcript'] = df['transcript'].str.replace("ʻ", '')
df['transcript'] = df['transcript'].str.replace("’", '')

df['transcript'] = df['transcript'].str.replace("-", ' ')
df['transcript'] = df['transcript'].str.replace(" – ", ' ')
df['transcript'] = df['transcript'].str.replace(" … ", ' ')

# Collapse multiple spaces
df['transcript'] = df['transcript'].str.replace(r' +', ' ')

train_set = df.iloc[0:-10000]
dev_set = df.iloc[-10000:-5000]
test_set = df.iloc[-5000:]

print('Samples in train set: {}'.format(len(train_set)))
train_duration = ((train_set['wav_filesize'] - 44) / 16000 / 2).sum()
print('Total duration in seconds: {}'.format(train_duration))

print('Samples in dev set: {}'.format(len(dev_set)))
dev_duration = ((dev_set['wav_filesize'] - 44) / 16000 / 2).sum()
print('Total duration in seconds: {}'.format(dev_duration))

print('Samples in test set: {}'.format(len(test_set)))
test_duration = ((test_set['wav_filesize'] - 44) / 16000 / 2).sum()
print('Total duration in seconds: {}'.format(test_duration))

print('Saving train CSV to {}'.format(args.train_dest))
train_set.to_csv(args.train_dest, encoding='utf8', index=False)

print('Saving dev CSV to {}'.format(args.dev_dest))
dev_set.to_csv(args.dev_dest, encoding='utf8', index=False)

print('Saving test CSV to {}'.format(args.test_dest))
test_set.to_csv(args.test_dest, encoding='utf8', index=False)



# normalization


# df2 = pandas.read_csv('all_dev.csv', encoding='utf8')

# df2['transcript'] = df2['transcript'].str.replace('ß', 'ss')
# df2['transcript'] = df2['transcript'].str.replace('ü', 'ue')
# df2['transcript'] = df2['transcript'].str.replace('ö', 'oe')
# df2['transcript'] = df2['transcript'].str.replace('ä', 'ae')

# df2['transcript'] = df2['transcript'].str.replace('í', 'i')
# df2['transcript'] = df2['transcript'].str.replace('á', 'a')
# df2['transcript'] = df2['transcript'].str.replace('ó', 'o')
# df2['transcript'] = df2['transcript'].str.replace('ú', 'u')
# df2['transcript'] = df2['transcript'].str.replace('ã', 'a')
# df2['transcript'] = df2['transcript'].str.replace('à', 'a')
# df2['transcript'] = df2['transcript'].str.replace('é', 'e')
