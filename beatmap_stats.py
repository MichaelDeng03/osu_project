import json
import dateutil.parser as dp
import time
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
import pandas as pd
from scipy.stats import linregress


def load_beatmaps(filename):
    '''
    Returns a dict of beatmaps from specified filename
    '''
    with open(filename, 'r', encoding='utf-16') as f:
        temp_dict = json.loads(f.read())
    return temp_dict


def save_beatmaps(dict, filename):
    with open(filename, 'w', encoding='utf-16') as f:
        f.write(json.dumps(dict))


def run_modifications():
    '''
    Runs all modifications and saves to beatmap_stats_modified.json
    '''
    global beatmaps_modified
    beatmaps_modified = load_beatmaps('beatmap_data.json')

    for beatmap_id in beatmaps_modified:
        # ADDS TIME SINCE RANKED
        ranked_date = beatmaps_modified[beatmap_id]['beatmapset']['ranked_date']
        if ranked_date is not None:
            ranked_date_seconds = dp.parse(ranked_date).timestamp()
            cur_time_seconds = time.time()
            days_elapsed = (cur_time_seconds - ranked_date_seconds)/(24 * 3600)
            beatmaps_modified[beatmap_id]['days_elapsed'] = days_elapsed
        else:
            beatmaps_modified[beatmap_id]['days_elapsed'] = None

        # ADDS PLAYCOUNT PER DAY
        playcount = beatmaps_modified[beatmap_id]['playcount']
        beatmaps_modified[beatmap_id]['playcount_per_day'] = playcount/days_elapsed

        # CONVERTS TO MINIMAL
        cur_beatmap = beatmaps_modified[beatmap_id]
        cur_minimal_beatmap = {}

        cur_minimal_beatmap['difficulty_rating'] = cur_beatmap['difficulty_rating']
        cur_minimal_beatmap['total_length'] = cur_beatmap['total_length']
        cur_minimal_beatmap['accuracy'] = cur_beatmap['accuracy']
        cur_minimal_beatmap['ar'] = cur_beatmap['ar']
        cur_minimal_beatmap['bpm'] = cur_beatmap['bpm']
        cur_minimal_beatmap['cs'] = cur_beatmap['cs']
        cur_minimal_beatmap['drain'] = cur_beatmap['drain']
        cur_minimal_beatmap['passcount'] = cur_beatmap['passcount']
        cur_minimal_beatmap['playcount'] = cur_beatmap['playcount']
        cur_minimal_beatmap['days_elapsed'] = cur_beatmap['days_elapsed']
        cur_minimal_beatmap['playcount_per_day'] = cur_beatmap['playcount_per_day']
        cur_minimal_beatmap['set_favorite_count'] = cur_beatmap['beatmapset']['favourite_count']
        cur_minimal_beatmap['set_playcount'] = cur_beatmap['beatmapset']['play_count']
        beatmaps_modified[beatmap_id] = cur_minimal_beatmap

    # REMOVES NONES
    to_remove = []
    for beatmap_id in beatmaps_modified:
        for key in beatmaps_modified[beatmap_id]:
            if beatmaps_modified[beatmap_id][key] == None:
                to_remove.append(beatmap_id)
    for beatmap_id in list(set(to_remove)):
        beatmaps_modified.pop(beatmap_id, None)

    save_beatmaps(beatmaps_modified, 'beatmap_stats_modified.json')


def convert_to_pandas(filename):
    '''
    Returns a dataframe constructed the json data in filename
    '''
    beatmaps = load_beatmaps(filename)
    return pd.DataFrame.from_dict(beatmaps).transpose()


def scatter_plot(df, x, y, logx, logy):
    '''
    Plots every x and y value with regression line
    '''
    f, ax = plt.subplots()

    plt.xlabel(' '.join(x.split('_')).title())  # prettify
    plt.ylabel(' '.join(y.split('_')).title())
    plt.title(' '.join(x.split('_')).title() + " vs. " + ' '.join(y.split('_')).title())
    x = df[x].to_numpy(dtype=float)
    y = df[y].to_numpy(dtype=float)

    # Scatter plot
    plt.scatter(x=x, y=y, color='black')

    # Linear regression line
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    plt.plot(x, slope*x+intercept, color='red')

    # Text with result of regression
    text = "r: " + str(round(r_value, 5)) + "\np: " + str(round(p_value, 5))
    plt.text(.83, 0.99, s=text, verticalalignment='top', transform=ax.transAxes)


def bar_plot(df, x, y, barcount):
    '''
    Plots a bar_plot of the average value of y for x values
    '''
    f, ax = plt.subplots()

    plt.xlabel(' '.join(x.split('_')).title())  # prettify
    plt.ylabel(' '.join(y.split('_')).title())
    plt.title(' '.join(x.split('_')).title() + " vs. " + ' '.join(y.split('_')).title())

    # Combine x and y, so that x can be sorted
    combined = np.array([list(df[x]), list(df[y])], dtype=float).transpose()

    # Sort x (and y along with it)
    combined = combined[np.argsort(combined[:, 0])]

    # Graph
    max_val, min_val = combined[-1, 0], combined[0, 0]
    interval = (max_val - min_val)/barcount

    raw_data = {}
    for val in combined[:]:
        cur_section = int((val[0] - min_val) // interval)

        if cur_section not in raw_data:
            raw_data[cur_section] = []
            raw_data[cur_section].append(val[1])
        else:
            raw_data[cur_section].append(val[1])

    processed = {key: [np.mean(raw_data[key]), np.std(raw_data[key])/len(raw_data[key])**0.5] for key in raw_data}
    xvals = [(val - 1)*interval + min_val + interval*0.5 for val in processed]
    yvals = [processed[key][0] for key in processed]
    error = [processed[key][1] for key in processed]

    ax.bar(x=xvals, height=yvals, width=interval*0.9, yerr=error,
           align='center', alpha=0.5, ecolor='black', capsize=10)

    ax.yaxis.grid(True)
    ax.xaxis.grid(True)


def bar_plot_3d(df, x, y, z, barcount):
    '''
    Plots average z value for intervals of x and y based on barcount
    '''
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set_title(' '.join(x.split('_')).title() + " and " + ' '.join(y.split('_')).title() + " vs. " + ' '.join(z.split('_')).title())
    ax.set_xlabel(' '.join(x.split('_')).title())
    ax.set_ylabel(' '.join(y.split('_')).title())
    ax.set_zlabel(' '.join(z.split('_')).title())
    
    data = np.array(df[[x, y, z]], dtype=float)
    #max is too high for diff rating because of correct data. should probably remove outliers.
    max_x, min_x = max(df[x]), min(df[x])
    max_y, min_y = max(df[y]), min(df[y])
    x_interval = (max_x - min_x)/barcount
    y_interval = (max_y - min_y)/barcount

    data_dict = {x_section: {y_section: [] for y_section in range(
        barcount)} for x_section in range(barcount)}

    for d in data:
        x_section = (d[0] - min_x) // x_interval
        y_section = (d[1] - min_y) // y_interval
        if x_section == barcount:  # exactly max
            x_section -= 1
        if y_section == barcount:
            y_section -= 1

        data_dict[x_section][y_section].append(d[2])

    for x_key in data_dict:
        for y_key in data_dict:
            if len(data_dict[x_key][y_key]) > 0:
                data_dict[x_key][y_key] = np.mean(data_dict[x_key][y_key])
            else:
                data_dict[x_key][y_key] = 0

    _x = np.arange(barcount)
    _y = np.arange(barcount)
    _xx, _yy = np.meshgrid(_x, _y)
    x, y = _xx.ravel(), _yy.ravel()
    top = []

    for i in range(len(x)):
        x_val = x[i]
        y_val = y[i]
        top.append(data_dict[x_val][y_val])

    X = np.array([(val - 1)*x_interval + min_x + x_interval*0.5 for val in x])
    Y = np.array([(val - 1)*y_interval + min_y + y_interval*0.5 for val in y])

    np.array(top)
    bottom = np.zeros_like(top)
    width = x_interval * 0.5
    depth = y_interval * 0.5

    ax.bar3d(X, Y, bottom, width, depth, top, shade=True)


#run_modifications()
beatmaps_df = convert_to_pandas('beatmap_stats_modified.json')
#scatter_plot(beatmaps_df, 'bpm', 'playcount_per_day', False, False)
bar_plot(beatmaps_df, 'set_favorite_count', 'playcount', 10)
#bar_plot_3d(beatmaps_df, 'set_favorite_count', 'set_playcount', 'playcount', 10)
plt.show()
