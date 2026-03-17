from library import AgentManagement
from library import LibraryManagement
from library.OutputLogging import start_logging, stop_logging, OutputLogger
from library.ConfigManager import config

# Configuration
bme_agent = config.get("bme_agent")
bme_agent_library = config.get("bme_agent_library")
moderator_agent = config.get("bme_moderator")


start_logging("agent_configuration")
logger = OutputLogger()

##################################################################
logger.log_section("Main Agent Configuration", level=1)
##################################################################

logger.log_section("Agent Identifier", level=2)
logger.log(f"- Agent: {bme_agent}")

AgentManagement.agent_instructions(agent_id=bme_agent, new_instructions='bme_agent_instructions.md')
AgentManagement.set_agent_description(agent_id=bme_agent, description="Teaching and tech support agent for the Biology Meets Engineering (BME) high school program")
logger.log("✅ Agent configured successfully")

logger.log_section("Agent Library Configuration", level=2)
LibraryManagement.remove_all_documents_from_library(library_id=bme_agent_library, confirm=False)
LibraryManagement.upload_document('robot_details.md', library_id=bme_agent_library)
LibraryManagement.upload_document('programming_blocks.md', library_id=bme_agent_library)
AgentManagement.unassign_all_libraries_from_agent(agent_id=bme_agent)
AgentManagement.assign_library_to_agent(agent_id=bme_agent, library_id=bme_agent_library)
logger.log("🎉 Library configured successfully")

##################################################################
logger.log_section("Moderator Configuration", level=1)
##################################################################

logger.log_section("Moderator Agent Setup", level=2)
logger.log(f"- Moderator Agent: {moderator_agent}")

AgentManagement.agent_instructions( agent_id=moderator_agent, new_instructions='bme_moderator_instructions.md')
AgentManagement.set_agent_description(agent_id=moderator_agent, description="Content moderator and privacy protector for BME chat system")
logger.log("✅ Moderator agent configured successfully")

stop_logging()
