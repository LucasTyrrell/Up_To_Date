import uuid


from models import model, validation_agent
from Tools import search
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
import datetime

from typing import TypedDict, Literal

from response_classifiers import QueriesClassifier, HTMLClassifier
from industries import INDUSTRIES

from bs4 import BeautifulSoup


#defines the information that is to be passed to each LLM call
class State(TypedDict):
        sub_sector: str | None
        industry: str | None
        queries: list[str] | None
        findings: list[str] | None
        valid_findings: bool | None
        reason: str | None
        retries: int | None
        summary: str | None
        HTML: str | None

#creates the queries to be sent to the LLM
def define_queries(state: State):
    try:
        sector = state.get('sub_sector')
        industry = state.get('industry')
        trusted_sites = INDUSTRIES[industry][sector]
        retries = state.get('retries') or 0
        reason = state.get('reason') or ''
        if retries == 0:
            system_message = (f'Create 5 - 10 search queries to be used to gather information for a newsletter, the information gathered is to be relevant to university students studying a degree of the following industry: [{industry}]'
                       f'the queries are to be returned in the form of a list of strings, only the following sites are to be explored: [{trusted_sites}] ')
        else:
            system_message = (f'Create 5 - 10 search queries to be used to gather information for a newsletter, the information gathered is to be relevant to university students studying a degree of the following industry: [{industry}]'
                       f'The queries developed last time lead to rejected information for the following reason: [{reason}. This is retry number [{retries}] the closer the retries is to 3 expand the scope past the trueted sites: [{trusted_sites}] ')
        structured_llm = model.with_structured_output(QueriesClassifier)

        response = structured_llm.invoke(
            [{'role': 'user', 'content': system_message}]
        )

        return {'queries': response.queries}
    except Exception as e:
            return {"summary": f"Error: {e}"}

#allows the agent to search for the queries provided by define_queries
def search_news(state: State):
        try:
            queries = state.get('queries') or []
            findings = [search.invoke(query) for query in queries]
            return {'findings': findings}

        except Exception as e:
                return {"summary": f"Error: {e}"}

#verify whether the information gathered is relevant, up to date and correct
def validate_findings(state: State):
        try:
            findings = state.get('findings')
            industry = state.get('industry')
            sector = state.get('sub_sector')
            retries = state.get('retries') or 0
            message = (f"These are the findings of the previouse node: [{findings}]."
                       f"This is the current date: [{datetime.datetime.now()}] the information should be no older than 1 month"
                       f"This is the industry: [{industry}] and this is the sector: [{sector}]")

            response = validation_agent.invoke({'messages': [{'role': 'user', "content": message}]})
            validation = response['structured_response']
            if not validation.valid:
                retries += 1
                return {'valid_findings': validation.valid, 'reason': validation.reason, 'retries': retries}
            else:
                return {'valid_findings': validation.valid}
        except Exception as e:
                return {"summary": f"Error: {e}", "retries": (state.get('retries') or 0) + 1}


#summarise findings into a digestible format
def summarise(state: State):
        try:
            findings = state.get('findings')
            sector = state.get('sub_sector')
            industry = state.get('industry')
            message = (f"Here are the findings: [{findings}]. Write this up as a newsletter section for a university student "
                       f"studying a degree in the industry: [{industry}], covering recent events in this sector: [{sector}]. "
                       f"Write in full, flowing prose, not bullet points or fragmented lists. Group related findings into "
                       f"well-structured paragraphs that read naturally, the way a newsletter article would. "
                       f"Simplify the language without removing any key details or anything vital for the student to "
                       f"understand the concept. If there are distinct topics, give each its own short title followed by "
                       f"a coherent paragraph (or a few short paragraphs) of narrative text under it.")

            response = model.invoke([{'role': 'user', 'content': message}])
            return {'summary': response.content}
        except Exception as e:
                return {"summary": f"Error: {e}"}

#forms the loop for further research
def validation_route(state: State) -> Literal['define_queries', 'summarise']:
    if state.get('valid_findings') or (state.get('retries') or 0) >= 3:
        return 'summarise'
    else:
        return 'define_queries'

def HTML_generator(state: State):
    try:
        content = state.get('summary')
        sector = state.get('sub_sector')
        industry = state.get('industry')
        structured_llm = model.with_structured_output(HTMLClassifier)

        system_message = '''You are to take the summary generated from searching the web, and return raw HTML structured in the form of a newsletter
                            The newsletter should look professional, have clear titles and defined sections.'''
        user_message = f'This is the industry; [{industry}] This is the sub sector: [{sector}] This is the summary: [{content}]'

        response = structured_llm.invoke([{'role': 'system', 'content': system_message}, {'role': 'user', 'content': user_message}])

        HTML = BeautifulSoup(response.HTML, 'html.parser').prettify()
        return {'HTML': HTML}
    except Exception as e:
        return {"summary": f"Error: {e}"}



graph_builder = StateGraph(State)

#defines the functions created as nodes that can be visited in the graph
graph_builder.add_node('define_queries', define_queries)
graph_builder.add_node('search_news', search_news)
graph_builder.add_node('validate_findings', validate_findings)
graph_builder.add_node('summarise', summarise)
graph_builder.add_node('validation_route', validation_route)
graph_builder.add_node('HTML_generator', HTML_generator)

#creates the graph, saying which nodes to visit next
graph_builder.add_edge(START, 'define_queries')
graph_builder.add_edge('define_queries', 'search_news')
graph_builder.add_edge('search_news', 'validate_findings')
graph_builder.add_conditional_edges('validate_findings', validation_route, {'summarise': 'summarise', 'define_queries': 'define_queries'})
graph_builder.add_edge('summarise', 'HTML_generator')
graph_builder.add_edge('HTML_generator', END)
checkpointer = InMemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)

config = {'configurable': {'thread_id': uuid.uuid4()}}

# TEMPORARY - remove once the graph is confirmed working end-to-end
if __name__ == "__main__":
    test_state = {
        "sub_sector": "AI and Machine Learning",
        "industry": "Computer Science",
        "queries": None,
        "findings": None,
        "valid_findings": None,
        "reason": None,
        "retries": None,
        "summary": None,
        "HTML": None
    }
    result = graph.invoke(test_state, config=config)
    print("Queries:", result.get("queries"))
    print("Valid findings:", result.get("valid_findings"))
    print("Retries used:", result.get("retries"))
    print("Summary:\n", result.get("summary"))
    print("HTML:\n", result.get("HTML"))
