from langgraph.graph import StateGraph, START, END

from agents.newsletter.newsletter_nodes.Scout.Scouts import CompanyScout, RoleScout, NewsScout, InterviewScout
from agents.newsletter.newsletter_nodes.document_generator_node import DocumentGenerator
from agents.newsletter.newsletter_nodes.summary_node import Summary
from agents.newsletter.state import State


class Newsletter:
    def __init__ (self, state: State):

        #initialise classes
        self.company_scout = CompanyScout()
        self.role_scout = RoleScout()
        self.news_scout = NewsScout()
        self.interview_scout = InterviewScout()
        self.summary_node = Summary()
        self.document_builder = DocumentGenerator()


        self.graph = StateGraph(State)

        #initialise the nodes
        self.graph.add_node('company_scout', self.company_scout.run, defer=True)
        self.graph.add_node('interview_scout', self.interview_scout.run, defer=True)
        self.graph.add_node('role_scout', self.role_scout.run, defer=True)
        self.graph.add_node('news_scout', self.news_scout.run, defer=True)
        self.graph.add_node('summary_node', self.summary_node.run)
        self.graph.add_node('HTML_generator', self.document_builder.HTML_generator)
        self.graph.add_node('PDF_generator', self.document_builder.PDF_generator)

        #build the graph
        #start the researchers
        self.graph.add_edge(START, 'company_scout')
        self.graph.add_edge(START, 'interview_scout')
        self.graph.add_edge(START, 'news_scout')
        self.graph.add_edge(START, 'role_scout')

        #send information to be summarised
        self.graph.add_edge('company_scout', 'summary_node')
        self.graph.add_edge('interview_scout', 'summary_node')
        self.graph.add_edge('news_scout', 'summary_node')
        self.graph.add_edge('role_scout', 'summary_node')

        #turn the summary into the PDF file
        self.graph.add_edge('summary_node', 'HTML_generator')
        self.graph.add_edge('HTML_generator', 'PDF_generator')
        self.graph.add_edge('PDF_generator', END)

    def run(self):
        compiled_graph = self.graph.compile()
        return compiled_graph

    def print_graph(self):
        compiled_graph = self.graph.compile()
        compiled_graph.get_graph().draw_mermaid_png(output_file_path='../../assets/NewsletterGraph.png')

if __name__ == '__main__':
    graph = Newsletter(State)
    graph.print_graph()