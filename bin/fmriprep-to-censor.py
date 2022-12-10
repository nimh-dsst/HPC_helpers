#!/usr/bin/env python3
__doc__ = \
	'''
	This script will take a directory of fmriprep derivatives and generate censor files based on the arguments
	Output files will be organized as a BIDs tree
	'''

import os
import sys
import argparse
import json
import pandas as pd
import numpy as np
from glob import glob

class ParseSettings(object):
	def __init__(self, args):
		self.args = vars(args)
		self.fmriprep = self._get_fmriprep(self.args['fmriprep'])
		self.out = self._mkdir_out(self.args['out_dir'])
		self.subjs = self._get_subjs(self.fmriprep)
		self.old = self._is_old(self.args['fmriprep'])
		self.dvars = self._parse_thresh(self.args,'dvars')
		self.fd = self._parse_thresh(self.args,'fd')
		self.seg = self._parse_seg(self.args['seg'])
		self.stringent = self.args['stringent']

	def _get_fmriprep(self,fmriprep):
		'''
		check existence and read access to fmriprep directory
		return if all good
		'''
		if not os.access(fmriprep, os.R_OK):
			print(f'{fmriprep} either does not exist or you do not have permission to read it!')
			sys.exit(1)

		return fmriprep

	def _is_old(self,fmriprep):
		'''
		checks if we're dealing with old or new fmriprep directory structures
		'''
		subjs = glob(f'{fmriprep}/sub-*')
		subjs = [i.rsplit('/',1)[1] for i in subjs]
		old = False
		if os.path.isdir(f"{fmriprep}/{subjs[0]}/fmriprep"):
			old = True

		return old


	def _mkdir_out(self,out_dir):
		'''
		make top level out dir
		'''
		if not os.path.isdir(out_dir):
			try:
				os.mkdir(out_dir)
				return out_dir
			except:
				print('Error creating output directory')
				sys.exit(1)
		else:
			return out_dir

	def _get_subjs(self,fmriprep):
		'''
		get all the subjects in the fmriprep dir
		'''
		subjs = glob(f'{fmriprep}/sub-*')
		subjs = [i.rsplit('/',1)[1] for i in subjs]

		return subjs

	def _parse_thresh(self, args, thresh):
		'''
		make sure threshold is float
		'''
		if not args[thresh]:
			return None

		try:
			th = float(args[thresh])
		except:
			print(f'ERROR: Cannot convert {thresh} to float')
			sys.exit(1)

		return th

	def _parse_seg(self, seg):
		'''
		make sure segment length is int
		'''
		if not seg:
			return None

		try:
			se = int(seg)
		except:
			print('ERROR: Cannot convert segment length to int')
			sys.exit(1)

		return se

class CreateCensor(object):
	def __init__(self, settings):
		self.settings = settings

	def run(self):
		'''
		loop through subjects and create censor files
		'''
		for s in self.settings.subjs:
			print(s)
			if not os.path.isdir(f'{self.settings.out}/{s}'):
				os.mkdir(f'{self.settings.out}/{s}')

			ses = []
			if self.settings.old:
				subj_dir = f'{self.settings.fmriprep}/{s}/fmriprep/{s}'
			else:
				subj_dir = f'{self.settings.fmriprep}/{s}/{s}'

			for root,dirs,files in os.walk(subj_dir):
				for d in dirs:
					if 'ses-' in d:
						ses.append(d)

			if not ses:
				out_dir = f'{self.settings.out}/{s}/func'
				if not os.path.isdir(out_dir):
					os.mkdir(out_dir)

				self.func_cen(f'{subj_dir}/func', out_dir)
			else:
				for ss in ses:
					if not os.path.isdir(f'{self.settings.out}/{s}/{ss}'):
						os.mkdir(f'{self.settings.out}/{s}/{ss}')

					out_dir = f'{self.settings.out}/{s}/{ss}/func'
					if not os.path.isdir(out_dir):
						os.mkdir(out_dir)

					self.func_cen(f'{subj_dir}/{ss}/func', out_dir)

	def func_cen(self,func,out_dir):
		'''
		given a func dir, loop through functional runs to create censor
		'''
		# find the functional runs confounds
		cfs = [i for i in glob(f'{func}/*task-rest*desc-confounds_timeseries.tsv')]
		for cf_file in cfs:
			cf = pd.read_csv(cf_file, sep='\t')
			
			if self.settings.fd:
				fd_ts = cf.loc[:,'framewise_displacement']
				fd_ts = fd_ts.fillna(0)

				# find timepoints below the FD threshold and label them as 1's
				fd_cen = (fd_ts <= self.settings.fd).astype(int)

				if self.settings.stringent:
					# remove one before and two after
					fd_cen = fd_cen & np.append(fd_cen[1:],1) & np.append(1,fd_cen[:-1]) & np.append([1, 1], fd_cen[:-2])

			if self.settings.dvars:
				dvars_ts = cf.loc[:,'dvars']
				dvars_ts = dvars_ts.fillna(0)

				# find timepoints below the DVARS threshold
				dvars_cen = (dvars_ts <= self.settings.dvars).astype(int)

				if self.settings.stringent:
					dvars_cen = dvars_cen & np.append(dvars_cen[1:],1) & np.append(1,dvars_cen[:-1]) & np.append([1, 1], dvars_cen[:-2])

			if self.settings.fd and self.settings.dvars:
				# create union censor
				fin_cen = fd_cen & dvars_cen

			elif self.settings.fd and not self.settings.dvars:
				fin_cen = fd_cen

			elif not self.settings.fd and self.settings.dvars:
				fin_cen = dvars_cen

			if self.settings.seg:
				# find the segments
				segs = np.diff(np.pad(fin_cen,1,'constant'))
				seg_srt = np.where(segs == 1)[0]
				seg_end = np.where(segs == -1)[0]-1

				# if segment < discard segment length, set to 0
				for idx, val in enumerate(seg_srt):
					if (seg_end[idx]-seg_srt[idx]+1) < self.settings.seg:
						fin_cen[seg_srt[idx]:seg_end[idx]+1] = 0

			out_stem = cf_file.split('/')[-1].split('_desc-confounds')[0]
			out_file = f'{out_stem}_desc-censor_timeseries.tsv'
			if not os.path.isfile(f'{out_dir}/{out_file}'):
				np.savetxt(f'{out_dir}/{out_file}',fin_cen,fmt='%1.0f')

			out_dict_file = f'{out_stem}_desc-censor_timeseries.json'
			if not os.path.isfile(f'{out_dir}/{out_dict_file}'):
				out_dict = {}
				out_dict['timeseries_length'] = len(fin_cen)
				out_dict['censored_timepoints'] = sum(fin_cen == 0)
				out_dict['uncensored_timepoints'] = sum(fin_cen == 1)
				out_dict['percent_censored'] = out_dict['censored_timepoints']/out_dict['timeseries_length']
				out_dict['meanFD'] = sum(fd_ts)/len(fd_ts)
				out_dict['settings'] = {'fd_thresh': self.settings.fd, 'dvars_thresh': self.settings.dvars, 'segment': self.settings.seg, 'one_before_two_after': self.settings.stringent}

				with open(f'{out_dir}/{out_dict_file}', 'w') as f:
					json.dump(out_dict, f, indent=4)

def build_parser():
	parser = argparse.ArgumentParser(description=__doc__,add_help = True)

	parser.add_argument('--fmriprep', action='store', dest='fmriprep',
		help='Fmriprep derivative directory')

	parser.add_argument('--dvars', metavar='thresh', action='store', dest='dvars', type=float, default=None,
		help='DVARS threshold for censoring purposes')

	parser.add_argument('--fd', metavar='thresh', action='store', dest='fd', type=float, default=None,
		help='Framewise displacement threshold for censoring purposes')

	parser.add_argument('--seg', metavar='seg_length', action='store', dest='seg', type=int, default=None,
		help='Segment length that should be preseved for censoring.')

	parser.add_argument('--stringent', action='store_true', dest='stringent',
		help='Segment length that should be preseved for censoring.')

	parser.add_argument('--out-dir', metavar='directory', action='store', dest='out_dir',
		help='Output directory. Script will find the subject ID and store the output in /directory/sub-<subject ID>')

	return parser

def Main():
	parser = build_parser()
	args = parser.parse_args()
	settings = ParseSettings(args)
	if not settings.fd and not settings.dvars:
		print('Why are you here?')
		sys.exit(1)

	censor = CreateCensor(settings)
	censor.run()

if __name__ == '__main__':
	Main()