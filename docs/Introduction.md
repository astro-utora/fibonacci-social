# Introduction

The Fibonacci social is intended to setup collaboration between people based on verfied information, taken from them.

The main workflow of the web app is to accept information from users, verify it and then connect users.

App offers users a way to describe their portfolio or project initial state and then track the path of user personality or project development. For that Path Tree is designed. Users can also on-board collegues and define thier own Path Trees to track collegues progress during their joint work. That makes Fibonacci social scalable.

## Path Tree

Path Tree is intended to accept information from the users along thier path of personaloty or project development.
Path Tree is a tree of nodes with names, designiting the aspect of a portfolio / project. The node can optionally have a link to fillout.com questionary to gather information from the user. Not each aspect is suitable for a person or project, so user selects nodes based on their specific case. By selecting set of nodes the user selects one or several paths in the tree.

It the node has a fillout link, then the node children are not visible to the user until they fill the information and the information will be validated. So the workflow for the node with fillout link is next:
1. Start to fill information
2. Finish fillout form
3. Request infromation validation
4. Get validation or rejection
5. In case of rejection the user can update information and send request for validation again.

Admininstrators in admin settings has a tab to track user progress in Path Tree and validate their requests.

## User's project

User can create his own projects and define project Path Tree in the project settings.
User can invite other people into the project, and then the invited user will see the project in their project list.
The owner of the project can edit Path Tree. Other users can fill information in the Path Tree with the same workflow, as for the main tree.
The validation functionality is missing currently in project settings and should be implemented later.

## Validators

By default the administrator is a validator of the main Path Tree.
Project owners are validators of thier project's Path Tree.
Later other users can get validator role and appropriate UI for roles management should be developed.

## Portfolio and projects

Currently there is a one main Path Tree, aimed to accept user portfolio information
The second Path Tree for user's project information is highly demanded and should be implemented shortly. The second tree is intended for the projects that user owns, let's call it Project Onwer Path Tree.
User should be able to enter information into Project Onwer Path Tree for each project they have.

So for a project a user can fill Project Onwer Path Tree and can create his project Path Tree, which will be filled by project members.