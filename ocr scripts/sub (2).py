# Usage: python3 sub.py inputfilePath
import argparse
import datetime
in_srt_format = "%M:%S,%f"
out_srt_format = "%H:%M:%S,%f" # Hours, minutes, second, microseconds

def to_srt(time_string):
    '''Given a str of format xx:xx.xxx
    Turn it into             xx:xx,xxx'''
    return time_string.replace(".", ",")

def get_timestamp_string_with_shift(counter, text, start_time, running_time):
    # NOTE! Adds a 150 millisecond shift to times.
    start_time_orig = datetime.datetime.strptime(to_srt(start_time), in_srt_format)
    end_time_orig = datetime.datetime.strptime(to_srt(running_time), in_srt_format)
    shift = datetime.timedelta(milliseconds=150)
    new_start = start_time_orig + shift
    new_start = new_start.strftime(out_srt_format)[:-3] # For microseconds->milliseconds
    new_end = end_time_orig + shift
    new_end = new_end.strftime(out_srt_format)[:-3]
    return f"""{counter}
00:{new_start} --> 00:{new_end}
{text}"""

def cludge(in_path):
    with open(in_path, 'r', encoding='utf-8-sig') as f:
        input_text = f.readlines()
    start_time, cur_text = input_text[0].split("  ", 1) # Initial case
    running_time = start_time
    counter = 1
    for line in input_text:
        timestamp, text = line.split("  ", 1) # Only split based on the first double-space
        if text == cur_text:
            # If we're still on the same line, extend the time
            running_time = timestamp
        else:
            # If we've found new text, print the last line over its duration
            to_print = get_timestamp_string_with_shift(counter, cur_text, start_time, running_time)
            print(to_print)
            # and reset the current line/time being tracked
            cur_text = text
            start_time = timestamp
            running_time = timestamp
            counter += 1
            
    # Having concluded, we should still print out our remaining text:
    to_print = get_timestamp_string_with_shift(counter, cur_text, start_time, running_time)
    print(to_print)
        

if __name__ == "__main__":
    # Establish parser stuff
    parser = argparse.ArgumentParser(description="Cludge subtitle formats to stdout")
    parser.add_argument("inPath", help="Path to input file", type=str)
    args = parser.parse_args()
    cludge(args.inPath)



