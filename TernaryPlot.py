# -*- coding: utf-8 -*-
"""
@author: Bismarck Gomes Souza Junior
@date:   Sat Mar 15 09:30:52 2014
@email:  bismarckjunior@outlook.com
@brief:  Plots a Ternary graph.
"""
from __future__ import division
from scipy import interpolate
from PyQt4.QtGui import QColor
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import copy as cp


class TernaryAxis():
    def __init__(self, fig, type_='bottom'):
        self.type = type_
        if type_ == 'right':
            self.beg = (1, 0)
            self.end = (0.5, 0.5*np.sqrt(3))
            self.phi_tick = np.pi
            self.transform_tick_label = (0.01, -0.004)
            self.transform_label = (0.1, 0.03)
            self.label_rotation = -60
            self.ha_tick_label = 'left'
        elif type_ == 'left':
            self.beg = (0.5, 0.5*np.sqrt(3))
            self.end = (0, 0)
            self.phi_tick = -np.pi/3
            self.transform_tick_label = (-0.01, -0.004)
            self.transform_label = (-0.1, 0.03)
            self.label_rotation = 60
            self.ha_tick_label = 'right'
        else:
            self.beg = (0, 0)
            self.end = (1, 0)
            self.phi_tick = np.pi/3
            self.transform_tick_label = (0, -0.04)
            self.transform_label = (0, -0.07)
            self.label_rotation = 0
            self.ha_tick_label = 'center'

        #Initializing variables
        self.percentageOn = False
        self.gridOn = True
        self.inverseOn = False
        self.min_max = True   # plots 0.0 and 1.0

        #Creating axis
        self.ax = ax = fig.add_subplot(111, aspect='equal')
        ax.set_xticks(())
        ax.set_yticks(())
        ax.set_frame_on(False) 
        self.text = ax.text
        self.plots = {'ticks':[], 'ticks_label':[], 'grids':[], 'label':[], 'inverse':[]}
        self.set_ticks()
    
    def cla(self):
        '''Clears axis.'''
        self.remove('ticks')
        self.remove('ticks_label')
        self.remove('label')
        self.grid(False) 
        self.remove('inverse')
    
    def remove(self, plot):
        '''Removes the plot. plot=[ticks, labels, grids, label].'''
        if plot in self.plots and self.plots[plot]:
            for p in self.plots[plot]:
                try:
                    p.pop(0).remove()
                except:
                    try: p.remove()
                    except: pass
            self.plots[plot] = []
            return True
        else:
            return False
    
    def set_label(self, text, **kw):
        '''Sets the axis label.'''
        self.remove('label')   
        xy = (np.array(self.beg)+np.array(self.end))/2.+np.array(self.transform_label)
        if self.label_rotation:
            self.plots['label'] = [self.text(xy[0],xy[1], text, ha='center', va='center', rotation=self.label_rotation, **kw)]
        else:
            self.plots['label'] = [self.text(xy[0],xy[1], text, ha='center', va='top', **kw)]
    
    def get_label(self):
        '''Gets the label.'''
        return self.plots['label'][0].get_text() if self.plots['label'] else ''        
        
    def set_ticks(self, ticks=10, llen_ticks=0.01, lw_ticks=1.2):
        '''Sets ticks. 
        ticks: list or integer
        llen_ticks: line lenght
        lw_ticks: line width
        ''' 
        self.ticks = []
        self.labels = []
        try:  
            ticks = [i/ticks for i in range(ticks+1)]
        except: 
            ticks = list(ticks)
            ticks.sort()
        for tick in ticks:
            xy = np.array(self.beg) + tick*(np.array(self.end)-np.array(self.beg))
            self.ticks.append(tuple(xy))
            self.labels.append(tick)
        self.llen_ticks=llen_ticks
        self.lw_ticks = lw_ticks
        self.update()
   
    def grid(self, toggle=None, grid_ticks=None, **kw):
        '''Removes or plots the grids.'''
        self.gridOn = toggle if toggle else not self.gridOn
        for grid in self.plots['grids']:
            grid[0].set_visible(self.gridOn)
        if not self.plots['grids']:
        #Removing grids
#        self.remove('grids')
#        self.plots['grids'].set_visibility(False)
#        self.gridOn = False
#        if not(toggle==None and self.gridOn or not toggle):
            #Ploting grids
            self.gridOn = True
            #self.plots['grids'].set_visibility(True)
            self.grid_ticks = grid_ticks if grid_ticks else self.ticks
            if 'linestyle' not in kw: kw['linestyle'] = ':'
            if 'color' not in kw: kw['color'] = 'k'
            if 'lw' not in kw: kw['lw'] = '.5'
            for tick in self.grid_ticks:
                x1,y1 = tuple(tick)
                x2,y2 = self.__boundary_point(tick)
                plt_grid = self.ax.plot([x1,x2],[y1,y2], **kw)
                self.plots['grids'].append(plt_grid)

    def percentage(self, toggle=None):
        '''Changes to percentage or not.'''
        self.percentageOn = toggle if toggle else not self.percentageOn
        self.__plot_ticks_label()

    def remove_ticks_label(self):
        '''Removes ticks label.'''
        self.remove('ticks_label')
        if self.type=='right':
            transform = (0.035,0.02)
        elif self.type=='left':
            transform = (-0.035,0.02)
        else:
            transform = (0,-0.03)
        xy = (np.array(self.beg)+np.array(self.end))/2.+np.array(transform)
        if 'label' in self.plots and self.plots['label']:
            text = self.plots['label'][0].get_text()
            fp= self.plots['label'][0].get_font_properties()
            self.remove('label')
            if self.label_rotation:
                self.plots['label'] = [self.text(xy[0],xy[1], text, ha='center', va='center', rotation=self.label_rotation)]
            else:
                self.plots['label'] = [self.text(xy[0],xy[1], text, ha='center', va='top')]
            self.plots['label'][0].set_font_properties(fp)
        
    def __inverse(self):
        '''Changes the tick angle.'''
        self.inverseOn = not self.inverseOn
        if self.type == 'right':
            self.phi_tick = -2*np.pi/3 if self.inverseOn else np.pi
        elif self.type == 'left':
            self.phi_tick = 0 if self.inverseOn else -np.pi/3
        else:
            self.phi_tick = 2*np.pi/3 if self.inverseOn else np.pi/3
                    
    def inverse(self):
        '''Inverse the axis.'''
        self.__inverse()
        self.update()
    
    def plot_inverse_ticks(self):
        '''Plots the invese ticks.'''
        self.__inverse()
        self.__plot_ticks()
        self.__inverse()
                
    def update(self):
        '''Updates the graph.'''
        self.remove('ticks')
        self.remove('ticks_label')
#        self.remove('grids') 
        self.__plot_ticks()
        self.__plot_ticks_label()
        if self.gridOn: self.grid(True)        
   
    def __rect(self, r, phi):
        '''From polar coordinates to rectangle coordinates.'''
        return (r*np.cos(phi), r*np.sin(phi))
    
    def __plot_ticks(self):
        '''Plots the ticks. llen_ticks: line lenght. lw_ticks: line width'''
        for tick in self.ticks:
            if tick not in [(0,0),(1,0)] and (tick[0]!=0.5 or tick[1]==0): 
                x1,y1 = tuple(tick)
                x2,y2 = tuple(np.array(tick)+np.array(self.__rect(self.llen_ticks, self.phi_tick))) 
                plt_tick = self.ax.plot([x1,x2], [y1,y2], 'k-', lw=self.lw_ticks)
                self.plots['ticks'].append(plt_tick)
    
    def __plot_ticks_label(self):
        '''Plots the ticks label.'''
        if self.plots['ticks_label']:
            self.remove_ticks_label()
        for tick, label in zip(self.ticks, self.labels[::1-2*int(self.inverseOn)]):
            if not self.min_max:
                if tick in [(0,0),(1,0)] or tick[0]==0.5 and tick[1]!=0:
                    continue 
            xy_label = np.array(tick)+np.array(self.transform_tick_label)
            if self.percentageOn: label = '%g%%' % (label*100)
            plt_labels = self.text(xy_label[0], xy_label[1], label, ha=self.ha_tick_label, fontsize=11)
            self.plots['ticks_label'].append(plt_labels)
             
    def __boundary_point(self, xy):
        '''Finds the triangle boundary.'''
        x, y = tuple(xy)
        if x+y==0 or x+y==1:  return xy
        tan = np.tan(self.phi_tick)
        tan1 = np.tan(0)
        tan2 = np.tan(np.pi/3)
        tan3 = np.tan(2*np.pi/3)

        #Intersection with bottom line
        x1 = (y-tan*x)/(tan1-tan) if tan1 != tan else 2
        y1 = 0

        #Intersection with left line
        x2 = (y-tan*x)/(tan2-tan) if tan2 != tan else 2
        y2 = x2*tan2

        #Intersection with right line
        x3 = (-y+tan*x-tan3)/(tan-tan3)  if tan3 != tan else 2
        y3 = (x3-1)*tan3

        for a,b in [(x1,y1),(x2,y2),(x3,y3)]:
            if not (abs(a-x)<1E-3 and abs(b-y)<1E-3 ) and 0<=a<=1 and 0<=b<=1:
                return (a, b)                
        return (a, b)


class TernaryPlot():
    def __init__(self, fig=None, title='', main_labels=[], short_labels=[],
                 canvas=plt):
        #Setting figure
        if fig:
            self.fig = fig
        else:
            self.fig = plt.figure()
            
        mngr = plt.get_current_fig_manager()
        # to put it into the upper left corner for example:
        mngr.window.setGeometry(50,100,640, 545)

        #Clearing plot
        self.clear_plot()

        #Setting canvas
        self.canvas = canvas

        #Initializing some variables
        self.templates = []
        self.inverseOn = False
        self.min_maxOn = True
        self.gridOn = True
        self.plots = []
        self.properties = []
        self.short_labels_plot = []
#        self.legends_labels = []
        self.legends_visible = []
        self.__set_colors()

        #Setting and ploting title and labels
        self.title = title
        self.main_labels = main_labels
        self.short_labels = short_labels
        if title:
            self.set_title(title, fontsize=21)
        if main_labels:
            self.set_main_labels(main_labels, fontsize=13)
        if short_labels:
            self.set_short_labels(short_labels, d=0.98, fontsize=16)
            self.show_min_max(False)

    def __set_colors(self):
        '''Sets colors to plot.'''
        self.colors = ['#000000', '#ff0000', '#00ff00', '#0000ff', '#ffff00',
                       '#ff00ff', '#00ffff', '#ff8800', '#ff0088', '#ff8888',
                       '#88ff00', '#8800ff', '#8888ff', '#88ff88', '#00ff88',
                       '#0088ff', '#880000', '#008800', '#000088', '#888888']
        self.colors += [str(s) for s in QColor.colorNames()]

    def __generate_properties(self, **kw):
        '''Generates and returns properties for plot.'''
        props = {'marker': 'o', 'markersize': 6, 'linestyle': '', 
                 'label':'Group %d' % (len(self.plots)+1-len(self.templates))}
        for key in kw:
            props[key] = kw[key]
        if 'color' not in props:
            props['color'] = self.get_color()
        self.properties.append(props)
        return props

    def get_plot_visibility(self, index):
        '''Gets bool for plot visibility.'''
        if self.plots[index]:
            return self.plots[index][0].get_visible()
        else:
            return False
    
    def get_legend_visibility(self, index):
        '''Gets bool for legend visibility.'''
        return self.legends_visible[index]
    
    def set_legend_visibility(self, index, toggle):
        '''Sets legend visibility.'''
        if self.get_plot_visibility(index):
            self.legends_visible[index] = bool(toggle)
        self.legend()

    def set_plot_visibility(self, index, toggle):
        '''Sets plot visibility.'''
        if not self.plots[index]:
            return
        self.plots[index][0].set_visible(bool(toggle))
            
#        if self.legends_visible[index]:
#            if toggle:
#                self.legends_labels[index] = self.plots[index][0].properties()['label']
#            else:
#                self.legends_labels[index] = ''
#            self.legend()
        if self.legends_visible[index]:
            self.legends_visible[index] = bool(toggle)
        self.draw()
        
    def get_n(self):
        '''Gets the number of plots.'''
        return len(self.plots)

    def remove_plot(self, index):
        '''Removes plot.'''
#        if index>= len(self.plots):
#            self.plots.pop(index).remove()
#            self.colors = self.properties.pop(index)['color'] + self.colors
##            self.legends_labels.pop(index)
#            self.legends_visible.pop(index)
        if index >= len(self.plots):
            return
        self.set_legend_visibility(index, False)
        #self.plots[index][0].set_visible(False)
        self.plots[index][0].remove()
        self.colors = [self.properties[index]['color']] + self.colors

        if index in self.templates:
            self.templates.remove(index)
        if index == len(self.plots)-1:
            self.plots.pop()
            self.properties.pop()
            self.legends_visible.pop()
        else:
            self.plots[index] = []
            self.properties[index] = []
            self.legends_visible[index] = False

    def remove_data(self, index, data):
        x_plot = self.plots[index][0].get_xdata()
        y_plot = self.plots[index][0].get_ydata()
        xy_plot = zip(x_plot, y_plot)

        for x_, y_ in zip(*self.transform_points(data)):
            if (x_, y_) in xy_plot:
                i = xy_plot.index((x_, y_))
                xy_plot.pop(i)
                x_plot = np.delete(x_plot, i)
                y_plot = np.delete(y_plot, i)
        self.plots[index][0].set_data(x_plot, y_plot)
        if not x_plot:
            self.set_legend_visibility(index, False)
        
    def get_properties(self, index, key=None):
        '''Gets plot properties.'''
        if key:
            return cp.copy(self.properties[index][key])
        else:
            return cp.copy(self.properties[index])
    
    def change_properties(self, index, **kw):
        '''Changes properties plot.'''
        for key in kw:
            self.properties[index][key] = kw[key]
        self.update_plot()

    def get_color(self):
        '''Gets the next color.'''
        color = self.colors.pop(0)
        self.colors += color
        return color

    def set_title(self, title, **kw):
        '''Sets title.'''
        self.title = title
        self.__ax.set_title(title, **kw)

    def set_main_labels(self, labels, **kw):
        '''Sets main labels.'''
        for i, ax in enumerate(self.axes):
            ax.set_label(labels[i], **kw)

    def set_short_labels(self, labels, d=0.98, **kw):
        '''Sets the label on the  edges of the triangle.'''
        if self.min_maxOn:
            locations = [(0.5,0.91), (-0.06,-0.03), (1.06,-0.03)]
        else:
            locations = [(0.5,0.89), (-0.025,-0.03), (1.025,-0.03)]
        has = ['center', 'right', 'left']
        vas = ['bottom', 'center', 'center']
        if hasattr(self, 'short_title'):
            for i in range(3):
                self.short_labels_plot.pop().remove()
        else:
            self.short_title = []
        self.d_title(d)

        if not 'fontsize' in kw:
            kw['fontsize'] = 16

        for i, xy in enumerate(locations):
            short_label = self.__ax.text(xy[0], xy[1], labels[i], ha=has[i], va=vas[i], **kw)
            self.short_labels_plot.append(short_label)

    def transform_points(self, data):
        '''Transforms from x1,x2,x3 to x,y data and from x,y to x1,x2,x3 data.'''
        try:
            len(data[0])
        except:
            data = [data]
        
        if data and len(data[0]) == 3:
            data = np.matrix([[d/sum(row) for d in row] for row in data], np.float64)
            A = np.matrix([[.5, .5*np.sqrt(3)], [0, 0], [1, 0]])
            xy = np.array(data*A)
            return xy[:, 0], xy[:, 1]
        elif data and len(data[0]) == 2:
            data = np.matrix(data)
            A = np.matrix([[0, -np.sqrt(3), np.sqrt(3)], [2., -1, -1]])/np.sqrt(3)
            B = np.matrix([[0, 1, 0]]*len(data))
            xyz = np.array(data*A+B)
            return xyz[:, 0], xyz[:, 1], xyz[:, 2]

    def __plot_data(self, data, **kw):
        '''Plots data with the same settings.'''
        x, y = self.transform_points(data)
        kw = self.__generate_properties(**kw)
        return self.ax.plot(x, y, **kw)

    def plot_data(self, data, **kw):
        '''Plots data with the same settings and return the index.'''
        plot = self.__plot_data(data, **kw)
        self.plots.append(plot)
#        self.legends_labels.append(plot[0].properties()['label'])
        self.legends_visible.append(True)
        index = len(self.plots)-1
        return index

    def add_data(self, index, data):
        plot = self.plots[index][0]
        x_new, y_new = self.transform_points(data)
        x_old, y_old = plot.get_data()
        xy_new = zip(x_new, y_new)
        xy_old = zip(x_old, y_old)
        for i in range(len(x_new))[::-1]:
            if xy_new[i] in xy_old:
                x_new = np.delete(x_new, i)
                y_new = np.delete(y_new, i)
        x_new = np.append(x_old, x_new)
        y_new = np.append(y_old, y_new)
        kw = self.properties[index]
        plot.remove()
        self.plots[index] = self.ax.plot(x_new, y_new, **kw)
        self.update_plot(index)
        self.draw()

    def add_null_plot(self, **kw):
        '''Adds null plot.'''
        #self.legends_labels.append('')
        self.legends_visible.append(False)
        kw = self.__generate_properties(**kw)
        self.plots.append(plt.plot([],[], **kw))
        return len(self.plots)-1

    def update_axes(self):
        '''Updates axes and data.'''
        for ax in self.axes:
            ax.update()
        self.update_plot()
            
    def update_plot(self, index=None, data=None, **kw):
        '''Updates data plot.'''
        if index!=None:
            props = self.properties[index]
            for key in kw:
                props[key] = kw[key]
            self.properties[index] = props
#            self.legends_labels[index] = props['label']
            if data!=None:
                try:
                    self.plots[index][0].remove()
                except:
                    pass
                xy = self.transform_points(data)
                if xy:
                    self.plots[index] = self.ax.plot(*xy, **props)
                else:
                    self.plots[index] = self.ax.plot([],[], **props)
            else:
                self.plots[index][0].update(props)
        else:
            for index in range(len(self.plots)):
                props = self.properties[index]
                if self.plots[index][0]:
                    self.plots[index][0].update(props)
#        self.legend(self.legends_labels)
        self.legend()
        self.draw()

    def legends_labels(self):
        labels = []
        for props in self.properties:
            if props:
                labels.append(props['label'])
            else:
                labels.append('')
        return labels

    def legend(self, labels=None):
        '''Plots the legend.'''
        if labels:
            self.legends_labels = labels
            for i, label in enumerate(labels):
                self.properties[i]['label'] = label
                self.plots[i][0].set_label(label)
            labels = labels + self.legends_labels()[len(labels):]
        else:
            labels = self.legends_labels()
#        n = len(labels) if len(labels) < 13 else 13
        
        lines, labels_ = [], []
        lines_template, labels_template = [], []
        for index in range(len(self.plots)):
            line = self.plots[index]
            label = labels[index]
            b = self.legends_visible[index]
            if line and label and b:
                if not self.plots[index][0].get_xdata().any():
                    self.legends_visible[index] = False
                    continue
                if index in self.templates:
                    lines_template.append(line[0])
                    labels_template.append(label)
                else:
                    lines.append(line[0])
                    labels_.append(label)
        total_lines = lines+lines_template
        n = len(total_lines) if len(total_lines) < 13 else 13
        if total_lines:
            self.legends = self.ax.legend(total_lines, labels_+labels_template, loc=2,
                       numpoints=1, bbox_to_anchor=(0.70+0.03*n, .2, 1.2, 0.75))
        elif hasattr(self, 'legends'):
            self.legends.set_visible(False)

    def grid(self, toggle=None, **kw):
        '''Plots or removes the grids.'''
        for ax in self.axes:
            ax.grid(toggle, **kw)
        self.gridOn = ax.gridOn

    def percentage(self, toggle=None):
        '''Changes to percentage.'''
        for ax in self.axes:
            ax.percentage(toggle)
        self.update_axes()

    def inverse(self):
        '''Inverses the axes.'''
        A, B, C = tuple(self.get_main_labels())
        new_labels = [B, C, A] if self.inverseOn else [C, A, B]
        self.inverseOn = not self.inverseOn
        for ax, t in zip(self.axes, new_labels):
            ax.inverse()
            ax.set_label(t)

    def __plot_template(self, data, kind, **kw):
        '''Plots the template using linear or cubic interpolation.'''
        data.sort(key=lambda xyz: xyz[-1]/float(sum(xyz)))
        x, y = self.transform_points(data)
        if kind == 'fill':
            if 'fill' not in kw:
                kw['fill'] = False
            #hatch=['/' | '\' | '|' | '-' | '+' | 'x' | 'o' | 'O' | '.' | '*' ]
            template = self.ax.fill(x, y, **kw)
        else:
            if 'linestyle' not in kw:
                kw['linestyle'] = '-'
            if 'color' not in kw:
                kw['color'] = 'k'
            if 'lw' not in kw:
                kw['lw'] = 1.2
            if kind == 'linear':
                template = self.ax.plot(x, y, **kw)
            elif kind == 'cubic':
                f = interpolate.interp1d(x, y, kind)
                x_ = np.linspace(min(x), max(x), 50)
                template = self.ax.plot(x_, f(x_), **kw)
        if 'label' not in kw:
            kw['label'] = 'Template %d' % (len(self.templates)+1)
        self.properties.append(kw)
        return template

    def plot_template(self, data, kind='linear', **kw):
        '''Plots the template using linear or cubic interpolation and return 
        index.''' 
        template = self.__plot_template(data, kind, **kw)
        index = len(self.plots)
        self.plots.append(template)
        self.legends_visible.append(False)
        self.templates.append(index)
        return index
        
    def get_main_labels(self):
        '''Gets main labels.'''
        return [ax.get_label() for ax in self.axes]
        
    def show_min_max(self, toggle=None):
        '''Toggles between showing the minimum and maximum values or not.'''
        self.min_maxOn = toggle if toggle else not self.min_maxOn
        for ax in self.axes:
            ax.min_max = self.min_maxOn
            self.update_axes()
        if self.short_labels:
            fs = self.short_labels_plot[0].get_fontsize()
            self.set_short_labels(self.short_labels, d=0.98, fontsize=fs)
            
    def clear_plot(self, index = None):
        '''Clears the plot.'''
        if index!=None:
            self.remove_plot(index)
#            try:
#                self.plots[index][0].remove()
#                self.properties[index] = []
#                if index == len(self.plots)-1:
#                    self.plots.pop()
#                    self.properties.ppo()
#                else:
#                    self.plots[index] = []
#            except:
#                pass
        else:
            #Clearing figure
            self.fig.clf()
            
            #Clearing axes
            ax = self.fig.add_subplot(111, aspect='equal')
            ax.set_ylim(-0.01, 0.92)
            ax.set_xlim(-0, 1.01)
            self.d_title = lambda d: ax.set_ylim(-0.01, d)
            
            #Creating background
            p = patches.Polygon([(0,0),(0.5,0.5*np.sqrt(3)),(1,0),(0,0)], 
                                 facecolor="white",edgecolor="black", lw=1.)
            ax.add_patch(p)
            
            #Setting main axis
            self.__ax = ax
            self.ax = self.fig.add_subplot(111, aspect='equal')
            
            #Creating axes
            self.__create_axes()  
    
    def show(self):
        '''Shows the graphic.'''
        self.canvas.show()    
    
    def draw(self):
        '''Draws the graphic.'''
        self.canvas.draw()
        
    def __create_axes(self):
        '''Creates the axes.'''
        self.axRight = TernaryAxis(self.fig, 'right')
        self.axLeft = TernaryAxis(self.fig, 'left')
        self.axBottom = TernaryAxis(self.fig, 'bottom')
        self.axes = [self.axRight, self.axLeft, self.axBottom]
        
if __name__=='__main__':
    fig = plt.figure()       
    T = TernaryPlot(fig, 'Ternary Plot', ['Big A', 'Big B', 'Big C'], ['A','B','C'])
    #print dir(fig)
    ax= fig._get_axes()
    
    data = [ [10,20,70], [20,25,55], [0.5,0.2,0.3]]
    group1 = T.plot_data(data, color='green', label='Texto1')
    group2 = T.plot_data([[60,10,30],[25,5,70]])
    T1 = T.plot_template(data+[[40,50,10]],'fill', hatch='/', fill=False, edgecolor='k', color='c')
    T.legend()
    #T.set_title('Ok')
    #T.legend(['Sample 1', 'Sample 2'])
    #T.set_plot_visibility(group1, False)
    #T.set_plot_visibility(group2, True)
    #T.clear_plot(T1)
    #T.inverse()
    #T.update_plot(0, [], color='k', markersize=10, marker='o')
    #T.remove_plot(group2)
    T.set_legend_visibility(group1, False)
    #print dir(leg.texts[0])
    T.show()

    