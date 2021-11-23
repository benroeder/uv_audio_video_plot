import matplotlib.pyplot as plt
import parse
import numpy
import pprint
import argparse
import sys


def spinning_cursor():
    while True:
        for cursor in "|/-\\":
            yield cursor


spinner = spinning_cursor()


def spin(text):

    sys.stdout.write(text + " " + next(spinner))
    sys.stdout.flush()
    back_spc = (len(text) + 2) * "\b"
    sys.stdout.write(back_spc)


def graph(log_file, graph_audio=True, graph_video=True):

    pp = pprint.PrettyPrinter(indent=4)

    # eaxmple to parse
    # [1637574770.182] [Decklink display] putf - 0 frames buffered, lasted 3.4 ms.
    # [1637574770.134] [Decklink display] putf audio - lasted 0.088 ms.

    audio_timings = []
    video_timings = []
    audio_diff = []
    last_audio = 0.0
    bad_format_count = 0
    audio_count = 0
    line_count = 0

    with open(log_file, "r") as stderr_f:
        line = stderr_f.readline()
        while line:
            r = parse.search(
                "[{count}] [Decklink display] putf - 0 frames buffered, lasted {video_ms} ms.",
                line,
            )
            if r:
                try:
                    count = float(r["count"])
                    video_ms = float(r["video_ms"])
                    video_timings.append((count, video_ms))
                except:
                    bad_format_count = bad_format_count + 1
                    pass
            else:
                r = parse.search(
                    "[{count}] [Decklink display] putf audio - lasted {audio_ms} ms.",
                    line,
                )
                if r:
                    try:
                        count = float(r["count"])
                        audio_ms = float(r["audio_ms"])

                        audio_diff.append((audio_count, count - last_audio))
                        # print(audio_count)
                        last_audio = count

                        audio_timings.append((count, audio_ms))
                    except:
                        bad_format_count = bad_format_count + 1
                        pass
                    audio_count = audio_count + 1
            spin("Parsing line " + str(line_count))
            line_count = line_count + 1
            line = stderr_f.readline()

    ax, ay = zip(*audio_timings)
    x, y = zip(*video_timings)

    plt.xlabel("count")
    plt.ylabel("ms")
    if graph_video:
        plt.scatter(
            numpy.asarray(x), numpy.asarray(y), color="black", marker=",", lw=0, s=1
        )
    if graph_audio:
        plt.scatter(
            numpy.asarray(ax), numpy.asarray(ay), color="red", marker=",", lw=0, s=1
        )

    print("Bad format count = " + str(bad_format_count))

    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse timings from log file")
    parser.add_argument(
        "-l", "--logfile", help="log file path", default=None, required=True
    )
    parser.add_argument(
        "-a", "--audio", action="store_true", default=False, help="Plot audio"
    )

    parser.add_argument(
        "-v", "--video", action="store_true", default=False, help="Plot video"
    )
    args = parser.parse_args()
    graph_audio = args.audio
    graph_video = args.video
    log_file = args.logfile
    graph(log_file, graph_audio, graph_video)
