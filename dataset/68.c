struct attr_stack {
	struct attr_stack *prev;
	char *origin;
	size_t originlen;
	unsigned num_matches;
	unsigned alloc;
	struct match_attr **attrs;
};