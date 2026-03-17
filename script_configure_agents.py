from library import AgentManagement
from library import LibraryManagement
from library.OutputLogging import start_logging, stop_logging, OutputLogger
from library.ConfigManager import get_bme_agent, get_bme_agent_library

# Configuration
agent = get_bme_agent()
library = get_bme_agent_library()

start_logging("agent_configuration")
logger = OutputLogger()

logger.log_section("Agent Configuration", level=1)

logger.log_section("Agent Identifier", level=2)
logger.log(f"- Agent: {agent}")

AgentManagement.agent_instructions(agent_id=agent, new_instructions='bme_agent_instructions.md')
AgentManagement.set_agent_description(agent_id=agent, description="Teaching and tech support agent for the Biology Meets Engineering (BME) high school program")
logger.log("✅ Agent configured successfully")

logger.log_section("Agent Library Configuration", level=2)
LibraryManagement.remove_all_documents_from_library(library_id=library, confirm=False)
LibraryManagement.upload_document('robot_details.md', library_id=library)
LibraryManagement.upload_document('programming_blocks.md', library_id=library)
AgentManagement.unassign_all_libraries_from_agent(agent_id=agent)
AgentManagement.assign_library_to_agent(agent_id=agent, library_id=library)
logger.log("🎉 Library configured successfully")
stop_logging()
