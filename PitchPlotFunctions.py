import polars as pl
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import requests
from io import BytesIO
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from  matplotlib.ticker import FuncFormatter
import matplotlib.transforms as transforms
from matplotlib.patches import Ellipse
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.figure import Figure
import streamlit as st



class PitchPlotFunctions:
    # def __init__(self):
    #     self.name = name



    def pitch_colours(self):
        ### PITCH COLOURS ###
        pitch_colours = {
            ## Fastballs ##
            'FF': {'colour': '#FF007D', 'name': '4-Seam Fastball'},
            'FA': {'colour': '#FF007D', 'name': 'Fastball'},
            'SI': {'colour': '#98165D', 'name': 'Sinker'},
            'FC': {'colour': '#BE5FA0', 'name': 'Cutter'},

            ## Offspeed ##
            'CH': {'colour': '#F79E70', 'name': 'Changeup'},
            'FS': {'colour': '#FE6100', 'name': 'Splitter'},
            'SC': {'colour': '#F08223', 'name': 'Screwball'},
            'FO': {'colour': '#FFB000', 'name': 'Forkball'},

            ## Sliders ##
            'SL': {'colour': '#67E18D', 'name': 'Slider'},
            'ST': {'colour': '#1BB999', 'name': 'Sweeper'},
            'SV': {'colour': '#376748', 'name': 'Slurve'},

            ## Curveballs ##
            'KC': {'colour': '#311D8B', 'name': 'Knuckle Curve'},
            'CU': {'colour': '#3025CE', 'name': 'Curveball'},
            'CS': {'colour': '#274BFC', 'name': 'Slow Curve'},
            'EP': {'colour': '#648FFF', 'name': 'Eephus'},

            ## Others ##
            'KN': {'colour': '#867A08', 'name': 'Knuckleball'},
            'PO': {'colour': '#472C30', 'name': 'Pitch Out'},
            'UN': {'colour': '#9C8975', 'name': 'Unknown'},
        }

        # Create a dictionary mapping pitch types to their colors
        dict_colour = dict(zip(pitch_colours.keys(), [pitch_colours[key]['colour'] for key in pitch_colours]))

        # Create a dictionary mapping pitch types to their colors
        dict_pitch = dict(zip(pitch_colours.keys(), [pitch_colours[key]['name'] for key in pitch_colours]))


        return dict_colour, dict_pitch


    def sns_custom_theme(self):
        custom_theme =  {
        "axes.facecolor": "white",
        "axes.edgecolor": ".8",
        "axes.grid": True,
        "axes.axisbelow": True,
        "axes.labelcolor": ".15",
        "figure.facecolor": "#f9f9f9",
        "grid.color": ".8",
        "grid.linestyle": "-",
        "text.color": ".15",
        "xtick.color": ".15",
        "ytick.color": ".15",
        "xtick.direction": "out",
        "ytick.direction": "out",
        "lines.solid_capstyle": "round",
        "patch.edgecolor": "w",
        "patch.force_edgecolor": True,
        "image.cmap": "rocket",
        "font.family": ["sans-serif"],
        "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans", "Bitstream Vera Sans", "sans-serif"],
        "xtick.bottom": False,
        "xtick.top": False,
        "ytick.left": False,
        "ytick.right": False,
        "axes.spines.left": True,
        "axes.spines.bottom": True,
        "axes.spines.right": True,
        "axes.spines.top": True}

        
        colour_palette = ['#FFB000','#648FFF','#785EF0',
                    '#DC267F','#FE6100','#3D1EB2','#894D80','#16AA02','#B5592B','#A3C1ED']

        return custom_theme, colour_palette


    def team_logos(self):
        # List of MLB teams and their corresponding ESPN logo URLs
        mlb_teams = [
            {"team": "AZ", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/ari.png&h=500&w=500"},
            {"team": "ATL", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/atl.png&h=500&w=500"},
            {"team": "BAL", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/bal.png&h=500&w=500"},
            {"team": "BOS", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/bos.png&h=500&w=500"},
            {"team": "CHC", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/chc.png&h=500&w=500"},
            {"team": "CWS", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/chw.png&h=500&w=500"},
            {"team": "CIN", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/cin.png&h=500&w=500"},
            {"team": "CLE", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/cle.png&h=500&w=500"},
            {"team": "COL", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/col.png&h=500&w=500"},
            {"team": "DET", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/det.png&h=500&w=500"},
            {"team": "HOU", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/hou.png&h=500&w=500"},
            {"team": "KC", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/kc.png&h=500&w=500"},
            {"team": "LAA", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/laa.png&h=500&w=500"},
            {"team": "LAD", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/lad.png&h=500&w=500"},
            {"team": "MIA", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/mia.png&h=500&w=500"},
            {"team": "MIL", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/mil.png&h=500&w=500"},
            {"team": "MIN", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/min.png&h=500&w=500"},
            {"team": "NYM", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/nym.png&h=500&w=500"},
            {"team": "NYY", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/nyy.png&h=500&w=500"},
            {"team": "OAK", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/oak.png&h=500&w=500"},
            {"team": "PHI", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/phi.png&h=500&w=500"},
            {"team": "PIT", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/pit.png&h=500&w=500"},
            {"team": "SD", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sd.png&h=500&w=500"},
            {"team": "SF", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sf.png&h=500&w=500"},
            {"team": "SEA", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sea.png&h=500&w=500"},
            {"team": "STL", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/stl.png&h=500&w=500"},
            {"team": "TB", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tb.png&h=500&w=500"},
            {"team": "TEX", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tex.png&h=500&w=500"},
            {"team": "TOR", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tor.png&h=500&w=500"},
            {"team": "WSH", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/wsh.png&h=500&w=500"}
        ]

        # Create a DataFrame from the list of dictionaries
        df_image = pl.DataFrame(mlb_teams)
        # Set the index to 'team' and convert 'logo_url' to a dictionary
        image_dict  = df_image.select(['team', 'logo_url']).to_dict(as_series=False)['logo_url']

        # Convert to the desired dictionary format
        image_dict  = {row['team']: row['logo_url'] for row in df_image.select(['team', 'logo_url']).to_dicts()}

        return image_dict
    

    # Function to get an image from a URL and display it on the given axis
    def player_headshot(self,pitcher_id: str, ax: plt.Axes):
        # Construct the URL for the player's headshot image
        url = f'https://img.mlbstatic.com/mlb-photos/image/'\
            f'upload/d_people:generic:headshot:67:current.png'\
            f'/w_640,q_auto:best/v1/people/{pitcher_id}/headshot/silo/current.png'

        # Send a GET request to the URL
        response = requests.get(url)

        # Open the image from the response content
        img = Image.open(BytesIO(response.content))


        # Display the image on the axis
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 1)
        ax.imshow(img, extent=[0.2, 1.2, 0, 1], origin='upper')

        # Turn off the axis
        ax.axis('off')

    def player_bio(self,pitcher_id: str, ax: plt.Axes,start_date: str,end_date: str, batter_hand: list):
        # Construct the URL to fetch player data
        url = f"https://statsapi.mlb.com/api/v1/people?personIds={pitcher_id}&hydrate=currentTeam"

        # Send a GET request to the URL and parse the JSON response
        data = requests.get(url).json()

        # Extract player information from the JSON data
        player_name = data['people'][0]['fullName']
        pitcher_hand = data['people'][0]['pitchHand']['code']
        age = data['people'][0]['currentAge']
        height = data['people'][0]['height']
        weight = data['people'][0]['weight']

        # Display the player's name, handedness, age, height, and weight on the axis
        ax.text(0.5, 1, f'{player_name}', va='top', ha='center', fontsize=48)
        ax.text(0.5, 0.6, f'{pitcher_hand}HP, Age:{age}, {height}/{weight}', va='top', ha='center', fontsize=22)
        #ax.text(0.5, 0.35, f'2024 MLB Season', va='top', ha='center', fontsize=22, fontstyle='italic')

        if batter_hand == ['R']:
            batter_hand_text = ', vs RHH'

        elif batter_hand == ['L']:
            batter_hand_text = ', vs LHH'

        else:
            batter_hand_text = ''


        ax.text(0.5, 0.35, f'{start_date} to {end_date}{batter_hand_text}', va='top', ha='center', fontsize=22, fontstyle='italic')


        #ax.text(0.5, 0.35, f'2024 MLB Season', va='top', ha='center', fontsize=22, fontstyle='italic')

        # Turn off the axis
        ax.axis('off')

    def plot_logo(self,pitcher_id: str, ax: plt.Axes):
        # Construct the URL to fetch player data
        url = f"https://statsapi.mlb.com/api/v1/people?personIds={pitcher_id}&hydrate=currentTeam"

        # Send a GET request to the URL and parse the JSON response
        data = requests.get(url).json()

        # Construct the URL to fetch team data
        url_team = 'https://statsapi.mlb.com/' + data['people'][0]['currentTeam']['link']

        # Send a GET request to the team URL and parse the JSON response
        data_team = requests.get(url_team).json()

        # Extract the team abbreviation
        team_abb = data_team['teams'][0]['abbreviation']

        # Get the logo URL from the image dictionary using the team abbreviation
        try:
            logo_url = self.team_logos()[team_abb]

        except KeyError:
            logo_url = "https://a.espncdn.com/combiner/i?img=/i/teamlogos/leagues/500/mlb.png?w=500&h=500&transparent=true"

        # Send a GET request to the logo URL
        response = requests.get(logo_url)

        # Open the image from the response content
        img = Image.open(BytesIO(response.content))

        # Display the image on the axis
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 1)
        ax.imshow(img, extent=[0.8, 1.8, 0, 1], origin='upper')

        # Turn off the axis
        ax.axis('off')


    ### PITCH ELLIPSE ###
    def confidence_ellipse( self,
                            x:np.array,
                            y:np.array, 
                            ax:plt.Axes, 
                            n_std:float=3.0,
                            facecolor:str='none',
                            **kwargs):
        """
        Create a plot of the covariance confidence ellipse of *x* and *y*.
        Parameters
        ----------
        x, y : array-like, shape (n, )
            Input data.
        ax : matplotlib.axes.Axes
            The axes object to draw the ellipse into.
        n_std : float
            The number of standard deviations to determine the ellipse's radiuses.
        **kwargs
            Forwarded to `~matplotlib.patches.Ellipse`
        Returns
        -------
        matplotlib.patches.Ellipse
        """
        
        if x.shape != y.shape:
            raise ValueError("x and y must be the same size")
        try:
            cov = np.cov(x, y)
            pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
            # Using a special case to obtain the eigenvalues of this
            # two-dimensional dataset.
            ell_radius_x = np.sqrt(1 + pearson)
            ell_radius_y = np.sqrt(1 - pearson)
            ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                            facecolor=facecolor,linewidth=2,linestyle='--', **kwargs)
            

            # Calculating the standard deviation of x from
            # the squareroot of the variance and multiplying
            # with the given number of standard deviations.
            scale_x = np.sqrt(cov[0, 0]) * n_std
            mean_x = x.mean()
            

            # calculating the standard deviation of y ...
            scale_y = np.sqrt(cov[1, 1]) * n_std
            mean_y = y.mean()
            

            transf = transforms.Affine2D() \
                .rotate_deg(45) \
                .scale(scale_x, scale_y) \
                .translate(mean_x, mean_y)
            
            

            ellipse.set_transform(transf + ax.transData)
        except ValueError:
            return    
            
        return ax.add_patch(ellipse)


    ### BREAK PLOT ###
    def break_plot_big(self,df: pl.DataFrame, ax: plt.Axes):

            font_properties = {'size': 20}
            font_properties_titles = {'size': 32}
            font_properties_axes = {'size': 24}
        
            label_labels = df.sort(by=['prop','pitch_type'],descending=[False,True])['pitch_type'].unique()   
            j = 0
            dict_colour, dict_pitch = self.pitch_colours()
            custom_theme, colour_palette = self.sns_custom_theme()
            for label in label_labels:
                    subset = df.filter(pl.col('pitch_type') == label)
                    if len(subset) > 4:
                        try:
                            if df['pitcher_hand'][0] == 'R':
                                self.confidence_ellipse(subset['hb'], 
                                                subset['ivb'],
                                                ax=ax,
                                                edgecolor = dict_colour[label],
                                                n_std=2,
                                                facecolor=dict_colour[label],
                                                alpha=0.2)
                            if df['pitcher_hand'][0] == 'L':
                                self.confidence_ellipse(subset['hb']*-1, 
                                                subset['ivb'],
                                                ax=ax,
                                                edgecolor = dict_colour[label],
                                                n_std=2,
                                                facecolor=dict_colour[label],
                                                alpha=0.2)
                        except ValueError:
                            return
                        j=j+1
                    else:
                        j=j+1  
                    
            if df['pitcher_hand'][0] == 'R':
                sns.scatterplot(ax=ax,
                                    x=df['hb']*1,
                                    y=df['ivb']*1,
                                    hue=df['pitch_type'],
                                    palette=dict_colour,
                                    ec='black',alpha=1,
                                    zorder=2,
                                    s=50)
            if df['pitcher_hand'][0] == 'L':
                sns.scatterplot(ax=ax,
                                    x=df['hb']*-1,
                                    y=df['ivb']*1,
                                    hue=df['pitch_type'],
                                    palette=dict_colour,
                                    ec='black',alpha=1,
                                    zorder=2,
                                    s=50)                
            # if df['pitcher_hand'][0] == 'L':
            #     sns.scatterplot(ax=ax,x=df['hb']*1,y=df['ivb']*1,hue=df['pitch_type'],palette=pitch_colours,ec='black',alpha=1,zorder=2,s=50)

            ax.set_xlim((-25,25))
            ax.set_ylim((-25,25))

            ax.hlines(y=0,xmin=-50,xmax=50,color=colour_palette[8],alpha=0.5,linestyles='--',zorder=1)
            ax.vlines(x=0,ymin=-50,ymax=50,color=colour_palette[8],alpha=0.5,linestyles='--',zorder=1)
            ax.set_xlabel('Horizontal Break (in)', fontdict=font_properties_axes)
            ax.set_ylabel('Induced Vertical Break (in)', fontdict=font_properties_axes)
            ax.set_title("Short Form Pitch Movement Plot",fontdict=font_properties_titles)


            ax.get_legend().remove()


            # ax1.set_xticklabels(ax1.get_xticks(), fontdict=font_properties)
            ax.set_xticklabels(ax.get_xticks(), fontdict=font_properties)

            # ax1.set_yticklabels(ax1.get_yticks(), fontdict=font_properties)
            ax.set_yticklabels(ax.get_yticks(), fontdict=font_properties)



            #ax1.set_aspect('equal', adjustable='box')
            if df['pitcher_hand'][0] == 'R':
                ax.text(-24.5,-24.5,s='← Glove Side',fontstyle='italic',ha='left',va='bottom',
                        bbox=dict(facecolor='white', edgecolor='black'),fontsize=16,zorder=3)
                ax.text(24.5,-24.5,s='Arm Side →',fontstyle='italic',ha='right',va='bottom',
                            bbox=dict(facecolor='white', edgecolor='black'),fontsize=16,zorder=3)
                #ax.invert_xaxis()
            if df['pitcher_hand'][0] == 'L':
                ax.invert_xaxis()    
                ax.text(24.5,-24.5,s='← Arm Side',fontstyle='italic',ha='left',va='bottom',
                        bbox=dict(facecolor='white', edgecolor='black'),fontsize=16,zorder=3)
                ax.text(-24.5,-24.5,s='Glove Side →',fontstyle='italic',ha='right',va='bottom',
                            bbox=dict(facecolor='white', edgecolor='black'),fontsize=16,zorder=3)
            ax.set_aspect('equal', adjustable='box')
            #ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)))
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)))
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)))  

    ### BREAK PLOT ###
    def break_plot_big_long(self,df: pl.DataFrame, ax: plt.Axes):

            font_properties = {'size': 20}
            font_properties_titles = {'size': 32}
            font_properties_axes = {'size': 24}
        
            label_labels = df.sort(by=['prop','pitch_type'],descending=[False,True])['pitch_type'].unique()   
            dict_colour, dict_pitch = self.pitch_colours()
            custom_theme, colour_palette = self.sns_custom_theme()
            j = 0
            for label in label_labels:
                    subset = df.filter(pl.col('pitch_type') == label)
                    print(label)
                    if len(subset) > 4:
                        try:
                            if df['pitcher_hand'][0] == 'R':
                                self.confidence_ellipse(subset['hb'], 
                                                subset['vb'],
                                                ax=ax,
                                                edgecolor = dict_colour[label],
                                                n_std=2,
                                                facecolor=dict_colour[label],
                                                alpha=0.2)
                            if df['pitcher_hand'][0] == 'L':
                                self.confidence_ellipse(subset['hb']*-1, 
                                                subset['vb'],
                                                ax=ax,
                                                edgecolor = dict_colour[label],
                                                n_std=2,
                                                facecolor=dict_colour[label],
                                                alpha=0.2)
                        except ValueError:
                            return
                        j=j+1
                    else:
                        j=j+1  
                    
            if df['pitcher_hand'][0] == 'R':
                sns.scatterplot(ax=ax,
                                    x=df['hb']*1,
                                    y=df['vb']*1,
                                    hue=df['pitch_type'],
                                    palette=dict_colour,
                                    ec='black',alpha=1,
                                    zorder=2,
                                    s=50)
            if df['pitcher_hand'][0] == 'L':
                sns.scatterplot(ax=ax,
                                    x=df['hb']*-1,
                                    y=df['vb']*1,
                                    hue=df['pitch_type'],
                                    palette=dict_colour,
                                    ec='black',alpha=1,
                                    zorder=2,
                                    s=50)                
            # if df['pitcher_hand'][0] == 'L':
            #     sns.scatterplot(ax=ax,x=df['hb']*1,y=df['vb']*1,hue=df['pitch_type'],palette=pitch_colours,ec='black',alpha=1,zorder=2,s=50)

            ax.set_xlim((-40,40))
            ax.set_ylim((-80,0))

            ax.axhline(y=0,color=colour_palette[8],alpha=0.5,linestyle='--',zorder=1)
            ax.axvline(x=0,color=colour_palette[8],alpha=0.5,linestyle='--',zorder=1)
            ax.set_xlabel('Horizontal Break (in)', fontdict=font_properties_axes)
            ax.set_ylabel('Vertical Break (in)', fontdict=font_properties_axes)
            ax.set_title("Long Form Pitch Movement Plot",fontdict=font_properties_titles)


            ax.get_legend().remove()


            # ax1.set_xticklabels(ax1.get_xticks(), fontdict=font_properties)
            ax.set_xticklabels(ax.get_xticks(), fontdict=font_properties)

            # ax1.set_yticklabels(ax1.get_yticks(), fontdict=font_properties)
            ax.set_yticklabels(ax.get_yticks(), fontdict=font_properties)



            #ax1.set_aspect('equal', adjustable='box')
            if df['pitcher_hand'][0] == 'R':
                ax.text(-39.5,-79.5,s='← Glove Side',fontstyle='italic',ha='left',va='bottom',
                        bbox=dict(facecolor='white', edgecolor='black'),fontsize=16,zorder=3)
                ax.text(39.5,-79.5,s='Arm Side →',fontstyle='italic',ha='right',va='bottom',
                            bbox=dict(facecolor='white', edgecolor='black'),fontsize=16,zorder=3)
                #ax.invert_xaxis()
            if df['pitcher_hand'][0] == 'L':
                ax.invert_xaxis()    
                ax.text(39.5,-79.5,s='← Arm Side',fontstyle='italic',ha='left',va='bottom',
                        bbox=dict(facecolor='white', edgecolor='black'),fontsize=16,zorder=3)
                ax.text(-39.5,-79.5,s='Glove Side →',fontstyle='italic',ha='right',va='bottom',
                            bbox=dict(facecolor='white', edgecolor='black'),fontsize=16,zorder=3)
            ax.set_aspect('equal', adjustable='box')
            #ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)))
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)))
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)))

    ### BREAK PLOT ###
    def release_point_plot(self,df: pl.DataFrame, ax: plt.Axes):

            font_properties = {'size': 20}
            font_properties_titles = {'size': 32}
            font_properties_axes = {'size': 24}
            dict_colour, dict_pitch = self.pitch_colours()
            custom_theme, colour_palette = self.sns_custom_theme()        
            if df['pitcher_hand'][0] == 'R':
                sns.scatterplot(ax=ax,
                                    x=df['x0']*-1,
                                    y=df['z0']*1,
                                    hue=df['pitch_type'],
                                    palette=dict_colour,
                                    ec='black',alpha=1,
                                    zorder=2,
                                    s=50)
            if df['pitcher_hand'][0] == 'L':
                sns.scatterplot(ax=ax,
                                    x=df['x0']*1,
                                    y=df['z0']*1,
                                    hue=df['pitch_type'],
                                    palette=dict_colour,
                                    ec='black',alpha=1,
                                    zorder=2,
                                    s=50)                
            # if df['pitcher_hand'][0] == 'L':
            #     sns.scatterplot(ax=ax,x=df['hb']*1,y=df['vb']*1,hue=df['pitch_type'],palette=pitch_colours,ec='black',alpha=1,zorder=2,s=50)
            ax.add_patch(plt.Circle((0, 10/12-18), radius=18, edgecolor='black', facecolor='#a63b17'))
            ax.add_patch(plt.Rectangle((-0.5, 9/12), 1, 1/6, edgecolor='black', facecolor='white'))


            ax.set_xlim((-4,4))
            ax.set_ylim((0,8))

            ax.axhline(y=0,color=colour_palette[8],alpha=0.5,linestyle='--',zorder=1)
            ax.axvline(x=0,color=colour_palette[8],alpha=0.5,linestyle='--',zorder=1)
            ax.set_ylabel('Vertical Release (ft)', fontdict=font_properties_axes)
            ax.set_xlabel('Horizontal Release (ft)', fontdict=font_properties_axes)
            ax.set_title("Release Points - Catcher Perspective",fontdict=font_properties_titles)


            ax.get_legend().remove()


            # ax1.set_xticklabels(ax1.get_xticks(), fontdict=font_properties)
            ax.set_xticklabels(ax.get_xticks(), fontdict=font_properties)

            # ax1.set_yticklabels(ax1.get_yticks(), fontdict=font_properties)
            ax.set_yticklabels(ax.get_yticks(), fontdict=font_properties)



            #ax1.set_aspect('equal', adjustable='box')
            if df['pitcher_hand'][0] == 'L':
                ax.text(-3.95,0.05,s='← Glove Side',fontstyle='italic',ha='left',va='bottom',
                        bbox=dict(facecolor='white', edgecolor='black'),fontsize=16,zorder=3)
                ax.text(3.95,0.05,s='Arm Side →',fontstyle='italic',ha='right',va='bottom',
                            bbox=dict(facecolor='white', edgecolor='black'),fontsize=16,zorder=3)
                #ax.invert_xaxis()
            if df['pitcher_hand'][0] == 'R':
                ax.invert_xaxis()    
                ax.text(3.95,0.05,s='← Arm Side',fontstyle='italic',ha='left',va='bottom',
                        bbox=dict(facecolor='white', edgecolor='black'),fontsize=16,zorder=3)
                ax.text(-3.95,0.05,s='Glove Side →',fontstyle='italic',ha='right',va='bottom',
                            bbox=dict(facecolor='white', edgecolor='black'),fontsize=16,zorder=3)
            ax.set_aspect('equal', adjustable='box')
            #ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)))
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)))
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)))

    def df_to_polars(self,df_original: pl.DataFrame,
                     pitcher_id: str,
                     start_date: str,
                     end_date: str,
                     batter_hand: list):
        df = df_original.clone()
        df = df.filter((pl.col('pitcher_id') == pitcher_id) & 
                       (pl.col('is_pitch') & (pl.col('pitch_type').is_not_null())) &
                       (pl.col('game_date') >= start_date) &
                       (pl.col('game_date') <= end_date) &
                       (pl.col('batter_hand').is_in(batter_hand)))
        df = df.with_columns(
        prop_percent = (pl.col.is_pitch / pl.col.is_pitch.sum()).over("pitch_type"),
        prop = pl.col.is_pitch.sum().over("pitch_type"))
        return df
    


    def final_plot(self,df: pl.DataFrame,pitcher_id: str,plot_picker: str):
        sns.set_theme(style="whitegrid", rc=self.sns_custom_theme()[0])
        # Create a figure and a gridspec with 6 rows and 5 columns
        fig = plt.figure(figsize=(16, 16), dpi=400)
        gs = gridspec.GridSpec(6, 5,
                            figure=fig,
                            height_ratios=[0.00000000005, 5, 30, 5, 2, 0.00000000005],
                            width_ratios=[1, 10, 10, 10, 1])

        # Create subplots for player headshot, bio, and logo
        ax_headshot = fig.add_subplot(gs[1, 1])
        ax_bio = fig.add_subplot(gs[1, 2])
        ax_logo = fig.add_subplot(gs[1, 3])

        start_date = df['game_date'].min()
        end_date = df['game_date'].max()
        batter_hand = list(df['batter_hand'].unique())

        self.player_headshot(pitcher_id=pitcher_id, ax=ax_headshot)
        self.player_bio(pitcher_id=pitcher_id, ax=ax_bio,
                        start_date=start_date,
                        end_date=end_date,
                        batter_hand=batter_hand)
        self.plot_logo(pitcher_id=pitcher_id, ax=ax_logo)

        # Create subplot for the main plot
        ax_main_plot = fig.add_subplot(gs[2, :])

        # Create subplot for the legend
        ax_legend = fig.add_subplot(gs[3, :])
        ax_legend.axis('off')

        # Create subplot for the footer
        ax_footer = fig.add_subplot(gs[-2, :])

        # Plot the pitch movement plot
        if plot_picker == 'short_form_movement':
            self.break_plot_big(df, ax_main_plot)
        if plot_picker == 'long_form_movement':
            self.break_plot_big_long(df, ax_main_plot)
        if plot_picker == 'release_point':
            self.release_point_plot(df, ax_main_plot)


        # Sort the DataFrame and get unique pitch types
        items_in_order = list(df.sort(by=['prop', 'pitch_type'], descending=[True, True])['pitch_type'].unique(maintain_order=True))


        dict_colour, dict_pitch = self.pitch_colours()

        # Get the corresponding colors from the dictionary
        ordered_colors = [dict_colour[x] for x in items_in_order]
        items_in_order = [dict_pitch[x] for x in items_in_order]


        # Create custom legend handles with circles
        legend_handles = [mlines.Line2D([], [], color=color, marker='o', linestyle='None', markersize=8, label=label)
                        for color, label in zip(ordered_colors, items_in_order)]

        # Add legend to ax_legend
        ax_legend.legend(handles=legend_handles, bbox_to_anchor=(0.1, 0, 0.8, 0.5), ncol=5,
                        fancybox=True, loc='lower center', fontsize=8, framealpha=1.0, markerscale=2, prop={'size': 16})

        # Add footer text
        ax_footer.text(x=0.075, y=1, s='By: Thomas Nestico\n      @TJStats', fontname='Calibri', ha='left', fontsize=24, va='top')
        ax_footer.text(x=1-0.075, y=1, s='Data: MLB', ha='right', fontname='Calibri', fontsize=24, va='top')
        ax_footer.axis('off')

        # Create subplots for the borders
        ax_top_border = fig.add_subplot(gs[0, :])
        ax_left_border = fig.add_subplot(gs[:, 0])
        ax_right_border = fig.add_subplot(gs[:, -1])
        ax_bottom_border = fig.add_subplot(gs[-1, :])

        # Turn off the axes for the border subplots
        ax_top_border.axis('off')
        ax_left_border.axis('off')
        ax_right_border.axis('off')
        ax_bottom_border.axis('off')

        fig.tight_layout()
        fig.subplots_adjust(hspace=0.1, wspace=0.1)

        # Show the figure
        st.pyplot(fig)
        #return fig





    

