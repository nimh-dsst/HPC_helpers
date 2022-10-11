#!/usr/bin/env python3
__doc__ = \
	'''
	This script takes an fmriprep derivatives directory and combs through all of the subject's
	report html files for errors. It will return the number of subjects with no errors, the
	number of subjects with no html files, and the number of subjects with errors. In addition,
	It will write a json summary of the report, including the subject IDs for the various lists
	and a list of error summaries for each subject, if specified.
	'''

# written by dmoracze, 2021-04-XX

import os
import sys
import json
import argparse
from glob import glob
try:
    from bs4 import BeautifulSoup
except:
    print('Please install BeautifulSoup first:')
    print('$ pip install beautifulsoup4')
    sys.exit(1)

class ParseArgs(object):
	def __init__(self, args):
		self.args = vars(args)
		self.fmriprep = self._prep_fmriprep(self.args['fmriprep_dir'])
		self.out = self._prep_output(self.args)
		self.raw = self._prep_rawdata(self.args)

	def _prep_output(self, args):
		'''
		divide into directory and filename, if one is not provided use defaults
		check existence of directory
		'''
		if not args['out_file']:
			return None
		else:
			input_split = args['out_file'].rsplit('/',1)
			if len(input_split)==1:
				if not '.json' in input_split[0]:
					self.fname = f'{input_split[0]}.json'
				else:
					self.fname = input_split[0]

				self.outdir = os.getcwd()
			elif len(input_split)==2:
				if not '.json' in input_split[1]:
					self.fname = f'{input_split[1]}.json'
				else:
					self.fname = input_split[1]

				if os.path.isdir(input_split[0]):
					self.outdir = input_split[0]
				else:
					print('ERROR: output directory does not exist!')
					sys.exit(1)
			else:
				print('ERROR: could not parse --out-file option!')
				sys.exit(1)

		return self

	def _prep_fmriprep(self, fmriprep_dir):
		'''
		Read fmriprep directory, create a list of subjects, makes sure there is at least one
		'''
		# check if it's a directory
		if not os.path.isdir(fmriprep_dir):
			print('ERROR: fmriprep_dir is not a valid directory!')
			sys.exit(1)

		# make sure there is at least one subject directory
		dirs = glob(f'{fmriprep_dir}/sub*')
		if not len([d for d in dirs if os.path.isdir(d)])>=1:
			print(f'ERROR: No subject directories found in {fmriprep_dir}!')
			sys.exit(1)

		self.dir = fmriprep_dir
		# get the subject IDs
		self.subjs = [i.rsplit('/',1)[1] for i in dirs]

		return self

	def _prep_rawdata(self, args):
		'''
		If a rawdata directory was give, get the subjects to corss reference with fmriprep outputs
		'''
		if not args['rawdata']:
			return None
		else:
			raw = args['rawdata']
			# check if it's a directory
			if not os.path.isdir(raw):
				print('ERROR: rawdata dir is not a valid directory!')
				print('Skipping...')
				return None

			# make sure there is at least one subject directory
			dirs = glob(f'{raw}/sub*')
			if not len([d for d in dirs if os.path.isdir(d)])>=1:
				print(f'ERROR: No subject directories found in {raw}!')
				print('Skipping...')
				return None

			self.rawdir = raw
			# get the subject IDs
			self.rawsubjs = [i.rsplit('/',1)[1] for i in dirs]

			return self


class CreateReport(object):
	def __init__(self, settings):
		self.settings = settings

	def _find_html(self,subj):
		'''
		traverse the tree to find the subject's html
		'''
		html_file = None
		for root, dirs, files in os.walk(f'{self.settings.fmriprep.dir}/{subj}'):
			if f'{subj}.html' in files:
				html_file = f'{root}/{subj}.html'
		return html_file


	def run(self):
		'''
		create the report dict
		'''
		print(f'\n++ generating fmriprep report for {self.settings.fmriprep.dir}')
		# output containers
		self.fin = dict()
		no_html = []
		done = []
		html_err = []
		errors = []
		errors_dict = dict()
		summary = dict()
		tool_width = len(self.settings.fmriprep.subjs)
		# setup toolbar
		sys.stdout.write("[%s]" % (" " * tool_width))
		sys.stdout.flush()
		sys.stdout.write("\b" * (tool_width+1)) # return to start of line, after '['
		for i, s in enumerate(self.settings.fmriprep.subjs):
			sys.stdout.write('-')
			sys.stdout.flush()
			# find the subject's html
			html_file = self._find_html(s)
			if not html_file:
				no_html.append(s)
				pass
			else:
				# read in html
				html = open(html_file, 'r')
				soup = BeautifulSoup(html, 'html.parser')
				errs = soup.find(id='errors')
				try:
					# get the errors, if any
					if 'No errors to report!' in errs.text:
						done.append(s)
					else:
						errors_dict[s] = [s.text for s in errs.findAll('summary')]
						errors.append(s)
				except:
					html_err.append(s)

			if self.settings.raw:
				missing_subjs = list(set(self.settings.raw.subjs) - set(self.settings.fmriprep.subjs))

		sys.stdout.write("]\n") # this ends the progress bar

		# create summary
		summary['done'] = len(done)
		summary['html_error'] = len(html_err)
		summary['no_html'] = len(no_html)
		summary['subjs_w_errors'] = len(errors)
		if self.settings.raw:
			summary['missing_subjs'] = len(missing_subjs)
		# create final dict
		self.fin['summary'] = summary
		self.fin['done'] = done
		self.fin['html_error'] = html_err
		self.fin['no_html'] = no_html
		if self.settings.raw:
			self.fin['missing_subjs'] = missing_subjs
		self.fin['subjs_w_errors'] = errors
		self.fin['errors'] = errors_dict
		print('++ report finished')


	def write(self):
		'''
		write the report, either to stdout or json
		'''
		if self.settings.args['out_file']:
			self.out_dict = dict()
			self.out_dict['summary'] = self.fin['summary']
			if self.settings.args['subj_list']:
				self.out_dict['done'] = self.fin['done']
				self.out_dict['html_error'] = self.fin['html_error']
				self.out_dict['no_html'] = self.fin['no_html']
				self.out_dict['subjs_w_errors'] = self.fin['subjs_w_errors']
				if self.settings.raw:
					self.out_dict['missing_subjs'] = self.fin['missing_subjs']
			if self.settings.args['errors']:
				self.out_dict['errors'] = self.fin['errors']

			out_report = f'{self.settings.out.outdir}/{self.settings.out.fname}'
			print(f'++ writing report to {out_report}')
			with open(out_report, 'w') as file:
				json.dump(self.out_dict, file, indent=4)

			if not os.path.isfile(out_report):
				print('ERROR: report was not written!')

		# print summary
		print(f'\n{self.fin["summary"]["done"]} subjects completed with no errors')
		print(f'{self.fin["summary"]["html_error"]} subjects had errors with their html file')
		print(f'{self.fin["summary"]["no_html"]} subjects had no fmriprep html file')
		if self.settings.raw:
			print(f'{self.fin["summary"]["missing_subjs"]} subjects exist in rawdata but have no directory in fmriprep')
		print(f'{self.fin["summary"]["subjs_w_errors"]} subjects had fmriprep errors\n')


def build_parser():
	parser = argparse.ArgumentParser(description=__doc__,add_help = True)

	parser.add_argument('-e', '--errors', action='store_true',
		help='''
		Include a dict of errors from the fmriprep reports from each subject. 
		This dict will only include subjects with errors. The format will be a dict where the 
		subject ID is the key and the value is a list of errors for that subject.
		Report will only include the <summary> tag for each error, 
		you will have to look at the full report to see the full error.
		''')

	parser.add_argument('-s', '--subj_list', action='store_true',
		help='''
		Include a list of subject IDs in the output. A subject ID dict with two entries will be created:
		a list of subjects with no errors and a list of subjects with errors.
		''')

	parser.add_argument('-o', '--out-file', metavar='output', action='store', dest='out_file',
		help='''
		Output directory and file. Output will be saved in JSON format. 
		If no directory is provided, current directory will be used.
		To differentiate output directory from output file you must include the / character.
		If no filename is provided, a default name derived from the fmriprep directory will be used.
		If --out-file is not specified, output report will be printed to stdout.
		''')

	parser.add_argument('-r', '--rawdata', metavar='rawdata', action='store', dest='rawdata',
		help='''
		Rawdata directory. If this option is given, the script will compare the subjects in rawdata
		to the subjects in the fmriprep directory. It will then report if any subject directories are
		missing from the fmriprep directory.
		''')

	parser.add_argument('fmriprep_dir', action='store', type=str, 
		help='fmriprep derivatives directory.')

	return parser

def Main():
	parser = build_parser()
	args = parser.parse_args()
	settings = ParseArgs(args)
	report = CreateReport(settings)
	report.run()
	report.write()


if __name__ == '__main__':
	Main()