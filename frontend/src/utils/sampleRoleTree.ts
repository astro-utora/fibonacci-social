export const sampleRoleTree = {
  role: "Organization",
  subroles: [
    {
      role: "Management",
      filloutId: "mgmt-form-1",
      subroles: [
        {
          role: "Team Lead",
          filloutId: "team-lead-form",
          subroles: []
        }
      ]
    },
    {
      role: "Development",
      subroles: [
        {
          role: "Frontend",
          filloutId: "frontend-form",
          subroles: []
        },
        {
          role: "Backend",
          filloutId: "backend-form",
          subroles: []
        }
      ]
    }
  ]
} 