import sublime
import sublime_plugin
from sublime import Region, DRAW_NO_OUTLINE, DRAW_EMPTY

sync_running = False

def get_visibility_offset(view):
	visible_region = view.visible_region()
	return  visible_region.begin() - view.lines(visible_region)[0].begin()


def set_ruler_offset_from_visible(view):
	ruler_pos = 80
	offset = get_visibility_offset(view)
	# NOTE: round the ruler to the nearest multiple of 4 added to 80
	print("offset before", offset)
	offset += (4 - offset) % 4
	print("offset after", offset)
	actual_ruler_pos = ruler_pos + offset
	print("ruler pos", actual_ruler_pos)
	view.settings().set('rulers', [actual_ruler_pos])

class ScrollListener(sublime_plugin.EventListener):
	old_pos = None

	def on_text_command(self, view, command_name, args):
		if sync_running:
			self.old_pos = view.viewport_position()

	def on_post_text_command(self, view, command_name, args):
		if sync_running:
			new_pos = view.viewport_position()
			if self.old_pos is None:
				self.old_pos = new_pos
			if command_name != 'scroll_width':
				# NOTE: when locked, we get the new y pos, but not the new xpos
				view.set_viewport_position((self.old_pos[0], new_pos[1]), False)
				additional_offset = 0

			# NOTE: when locked, update the ruler with scroll width commands
			set_ruler_offset_from_visible(view)

class LockScrollCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global sync_running
		current_state = self.view.settings().get('lock_scroll')
		self.view.settings().set('lock_scroll', not current_state)
		sync_running = current_state

		if sync_running:
			set_ruler_offset_from_visible(self.view)
		else:
			self.view.settings().set('rulers', [])
