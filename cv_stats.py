import datetime
import os
import pandas
import sys


if __name__ == '__main__':
    LOCALES = next(os.walk(sys.argv[1]))[1]

    for locale in LOCALES:
        path = os.path.join(sys.argv[1], locale)

        valid = pandas.read_csv(os.path.join(path, 'cv_{}_valid.csv'.format(locale)), encoding='utf-8')
        invalid = pandas.read_csv(os.path.join(path, 'cv_{}_invalid.csv'.format(locale)), encoding='utf-8')

        print(locale)
        print(len(valid), 'valid samples')
        if len(valid):
            durations = (valid.loc[:, 'wav_filesize'] - 44) / (2*16000)
            print('{:>20s}'.format('total duration:'), str(datetime.timedelta(seconds=durations.sum())))
            print('{:>20s}'.format('mean duration:'), str(datetime.timedelta(seconds=durations.mean())))
            print('{:>20s}'.format('median duration:'), str(datetime.timedelta(seconds=durations.median())))
            _75, _90, _99, _100 = durations.quantile((.75, .90, .99, 1))
            print('{:>20s}'.format('75% duration:'), str(datetime.timedelta(seconds=_75)))
            print('{:>20s}'.format('90% duration:'), str(datetime.timedelta(seconds=_90)))
            print('{:>20s}'.format('99% duration:'), str(datetime.timedelta(seconds=_99)))
            print('{:>20s}'.format('max duration:'), str(datetime.timedelta(seconds=_100)))

        print(len(invalid), 'invalid samples')
        if len(invalid):
            durations = (invalid.loc[:, 'wav_filesize'] - 44) / (2*16000)
            print('{:>20s}'.format('total duration:'), str(datetime.timedelta(seconds=durations.sum())))
            print('{:>20s}'.format('mean duration:'), str(datetime.timedelta(seconds=durations.mean())))
            print('{:>20s}'.format('median duration:'), str(datetime.timedelta(seconds=durations.median())))
            _75, _90, _99, _100 = durations.quantile((.75, .90, .99, 1))
            print('{:>20s}'.format('75% duration:'), str(datetime.timedelta(seconds=_75)))
            print('{:>20s}'.format('90% duration:'), str(datetime.timedelta(seconds=_90)))
            print('{:>20s}'.format('99% duration:'), str(datetime.timedelta(seconds=_99)))
            print('{:>20s}'.format('max duration:'), str(datetime.timedelta(seconds=_100)))

        print('--------------')
