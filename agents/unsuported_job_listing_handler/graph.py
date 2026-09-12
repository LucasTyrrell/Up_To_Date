from langgraph.graph import StateGraph, START, END

from agents.unsuported_job_listing_handler.nodes import ListingGate, ListingExtractor
from agents.unsuported_job_listing_handler.state import UnsupportedListingState


#routes past extraction entirely if scraping already failed or the page isn't a job listing
def route_after_gate(state: UnsupportedListingState) -> str:
    if state.get('error'):
        return END
    return 'extract_listing'


class UnsupportedJobListingHandler:
    def __init__(self, state=UnsupportedListingState):
        self.listing_gate = ListingGate()
        self.extractor = ListingExtractor()

        self.graph = StateGraph(state)

        self.graph.add_node('is_job_listing', self.listing_gate.run)
        self.graph.add_node('extract_listing', self.extractor.run)

        self.graph.add_edge(START, 'is_job_listing')
        self.graph.add_conditional_edges('is_job_listing', route_after_gate, ['extract_listing', END])
        self.graph.add_edge('extract_listing', END)

    def run(self):
        compiled_graph = self.graph.compile()
        return compiled_graph