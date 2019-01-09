import time
import curses
from random import choice

def display_text(stdscr, text):
	stdscr.clear()
	stdscr.move(0, 0)
	stdscr.addstr(text)
	stdscr.refresh()

def display_board(stdscr, game=None):
	stdscr.clear()
	# lambda that will produce an output line from each game line
	make_out_line = lambda x : '|\t' + '\t|\t'.join(map(str, x)) + '\t|\n'

	# move the cursor and add stuff to the screen
	stdscr.move( 0, 0 )
	all_out_lines = map( make_out_line, game )
	for out_line in all_out_lines:
		stdscr.addstr(out_line)
	
	# sort of force output to the screen
	stdscr.refresh()

def get_stdscr():
	stdscr = curses.initscr()
	curses.noecho()
	curses.cbreak()
	stdscr.keypad(True)
	return stdscr

def end_app(stdscr):
	curses.nocbreak()
	stdscr.keypad(False)
	curses.echo()
	curses.endwin()

def random_fill(game):
	random_choices = []
	# get a tuple of squares that are empty
	for num_y, line in enumerate(game):
		for num_x, cell in enumerate(line):
			if cell == '---':
				random_choices.append((num_y, num_x))
	# if the list of squares is empty there is no free space
	# this means that the game should be unchanged
	if not random_choices:
		return game

	# use the random choice method of the random module to pick what to add
	spot_to_fill = choice(random_choices)
	num_to_fill = choice([2, 4])
	game[spot_to_fill[0]][spot_to_fill[1]] = num_to_fill
	return game

def calc_possible(game):
	possible = {}
	# calculate the game board after an up, down, left, or right move
	
	# RIGHT
	right = [calc_line(line) for line in copy_game(game)]
	if right != game:
		possible['KEY_RIGHT'] = right

	# LEFT
	left = [list(reversed(calc_line(list(reversed(line))))) for line in copy_game(game)]
	if left != game:
		possible['KEY_LEFT'] = left

	# UP
	up_copy = copy_game(game)
	rotated_game = [[line[i] for line in reversed(up_copy)] for i in range(len(up_copy))]
	up = [calc_line(line) for line in rotated_game]
	rerotated_up = [[line[i] for line in up] for i in reversed(range(len(up_copy)))]
	if rerotated_up != game:
		possible['KEY_UP'] = rerotated_up
	
	
	# DOWN
	down_copy = copy_game(game)
	rotated_game = [[line[i] for line in down_copy] for i in range(len(down_copy))]
	down = [calc_line(line) for line in rotated_game]
	rerotated_down = [[line[i] for line in down] for i in range(len(down_copy))]
	if rerotated_down != game:
		possible['KEY_DOWN'] = rerotated_down

	return possible

# assume that a line is a horizontal row of the game board
# calculate as though pushing to the right
def calc_line(line):
	# first handle the slide into empty space
	for spot in reversed(list(range(1, len(line)))):
		i = 1
		while line[spot] == '---' and spot-i >= 0:
			line[spot] = line[spot-i]
			line[spot-i] = '---'
			i+= 1

	# combine any tiles next to each other
	for spot in reversed(list(range(1, len(line)))):
		if line[spot] == line[spot-1] and line[spot] != '---':
			line[spot] = 2* line[spot]
			line[spot-1] = '---'

	# fill empty space
	for spot in reversed(list(range(1, len(line)))):
		i = 1
		while line[spot] == '---' and spot-i >= 0:
			line[spot] = line[spot-i]
			line[spot-i] = '---'
			i+=1
		
	return line

def copy_game(game):
	return [line[:] for line in game[:]]

def main():
	

	# initialize the stdscr ( this is a window obj )
	stdscr = get_stdscr()

	# create inital game board with all spaces empty
	game = [['---' for y in range(4)] for x in range(4)]

	# to start with the game must be filled with two tiles
	random_fill(game)
	random_fill(game)
	
	possible_moves = calc_possible(game)

	# while there are moves that can be made let the game play
	while possible_moves:
		# display the board
		display_board(stdscr, game)
		# get user input until is is valid/ will do something
		user_input = stdscr.getkey()
		while user_input not in possible_moves:
			user_input = stdscr.getkey()
			if user_input == 'q':
				end_app(stdscr)
				exit()
			elif user_input not in possible_moves:
				curses.flash()
		# set the board to the users choice
		game = possible_moves[user_input]
		random_fill(game)

		# recalculate possible moves
		possible_moves = calc_possible(game)

	# one final time display the board
	# without this the user cannot see the losing game board
	display_board(stdscr, game)
	curses.flash()
	time.sleep(2)
	display_text(stdscr, 'GAME OVER :(')
	time.sleep(4)
	
	# when ending the app reset the terminal
	end_app(stdscr)

if __name__ == '__main__':
	main()
