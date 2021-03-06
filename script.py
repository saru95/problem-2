import sys
from antlr4 import *
from tokenizer import *
import glob
from tqdm import tqdm
import itertools
from collections import defaultdict
from os.path import join
from math import log2

class TokenSequenceLCS():

  def __init__(self, files):
    self.files = files # list of files to be parsed
    self.tokens_record = [] # parsed tokens are stored here
    self.result = [] # result to be written to the file
    self.sequence_cache = defaultdict(lambda: 0) # maintains a record of the token sequences


  def get_all_subsequences(self, tokens=[]):
    '''
      This routine gets all the possible token sequences given a list of token and
      maintains a cache of their count.
    '''
    l = len(tokens)
    for i in range(l):
      for j in range(i, l):
        if (j + 1) - i == 1:  continue
        self.sequence_cache[tuple(tokens[i:j + 1])] += 1


  def perform_lcs_calculation(self):
    '''
      This routine find the all the common token sequences across all the files
      and generates the report.
    '''
    print('Fetching all the possible token sequences...')
    for tokens in tqdm(self.tokens_record):
      self.get_all_subsequences(tokens)

    print('Finding the common tokens across all files...')
    tokens_in_files = [''.join(tokens) for tokens in self.tokens_record]
    cache_keys = list(self.sequence_cache.keys())
    for token in tqdm(cache_keys):
      if self.sequence_cache[token] < len(self.tokens_record):
        del self.sequence_cache[token]
        continue
      for i in tokens_in_files:
        if ''.join(token) not in i:
          try: del self.sequence_cache[token]
          except: continue

    print('Generating the report....')
    for token, count in self.sequence_cache.items():
      if count == 1: continue
      length = len(token)
      score = log2(length) * log2(count)
      self.result.append([score, length, count, list(token)])
    self.result.sort(key=lambda x: x[0], reverse=True) # sort the final result by score


  def perform_tokenizing(self):
    '''
      This routine extracts the tokens from all the files using the lexer
      generated by antlr4 using C's grammar in grammar/C.g4. This routine also
      initiates the perform_lcs_calculation method.
    '''
    for file in self.files:
      contents = FileStream(file)
      lexer = CLexer(contents)
      token_stream = CommonTokenStream(lexer)
      token_stream.fill() # read till EOF
      tokens = [token.text for token in token_stream.tokens][:-1]
      self.tokens_record.append(tokens)
    print('All tokens are found!')
    self.perform_lcs_calculation()


  def write_to_tsv(self, filename):
    '''
      This routine write's the result to a tab-separated file.
    '''
    try:
      print('Writing to the TSV file....')
      with open(f'{filename}.tsv', 'w') as file:
        file.write('score\ttokens\tcount\tsequence\n')
        for line in self.result:
          file.write(f'{line[0]}\t{line[1]}\t{line[2]}\t{line[3]}\n')
    except:
      print('Invalid name or path.')


if __name__ == '__main__':
  files = []
  tsv_name = sys.argv[1]
  if len(sys.argv) > 2:
    files = sys.argv
    files.pop(0); files.pop(0)
  else:
    path = input('Enter the directory path of source code files: ')
    files = glob.glob(join(path, "*.c"))

  t = TokenSequenceLCS(files)
  t.perform_tokenizing()
  t.write_to_tsv(filename=tsv_name)