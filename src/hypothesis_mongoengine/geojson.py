from hypothesis import strategies as st


__all__ = ("points", "line_strings", "polygons")


def points():
    return st.tuples(
        st.floats(min_value=-180.0, max_value=180.0),
        st.floats(min_value=-90.0, max_value=90.0),
    )


@st.composite
def line_strings(draw, closed=False):  # pragma: no cover
    # Hypothesis uses coverage internally, and this function, which is only
    # ever excuted during a draw, isn't reported as covered.
    line_string = draw(st.lists(points(), min_size=1))
    if closed:
        line_string.append(line_string[0])
    return line_string


def polygons():
    return st.lists(line_strings(closed=True), min_size=1)
