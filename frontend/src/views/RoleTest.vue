<template>
  <div class="role-test-container">
    <h2>Role Tree Editor</h2>
    <div class="editor-container">
      <json-object :data="testData" :field-name="'root'" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from '@vue/runtime-core'
import JsonObject from '@/components/roleTree/JsonObject.vue'

// Sample test data
const testData = ref({
    "roots": [
        {
            "role": "Stage 0: Newborn",
            "filloutId": null,
            "subroles": [
                {
                    "role": "Stage 55: Mid to Late Adult (35-55 years)",
                    "filloutId": null,
                    "subroles": [
                        {
                            "role": "Advanced Career Path",
                            "filloutId": null,
                            "subroles": [
                                {
                                    "role": "Executive Education Courses",
                                    "filloutId": null,
                                    "subroles": []
                                },
                                {
                                    "role": "Senior Management / Leadership",
                                    "filloutId": null,
                                    "subroles": []
                                }
                            ]
                        },
                        {
                            "role": "Family & Personal Growth",
                            "filloutId": null,
                            "subroles": [
                                {
                                    "role": "Raising Children (if any)",
                                    "filloutId": null,
                                    "subroles": []
                                },
                                {
                                    "role": "Financial Planning & Investments",
                                    "filloutId": null,
                                    "subroles": [
                                        {
                                            "role": "Banking Upgrades (Wealth Management)",
                                            "filloutId": null,
                                            "subroles": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "role": "Stage 21: Late Teen / Young Adult (16-21 years)",
                    "filloutId": null,
                    "subroles": [
                        {
                            "role": "High School (Grade 9-12)",
                            "filloutId": null,
                            "subroles": [
                                {
                                    "role": "College Entrance",
                                    "filloutId": null,
                                    "subroles": []
                                },
                                {
                                    "role": "Exam Preparations",
                                    "filloutId": null,
                                    "subroles": []
                                }
                            ]
                        },
                        {
                            "role": "First Jobs / Internships",
                            "filloutId": null,
                            "subroles": [
                                {
                                    "role": "Open Bank Account",
                                    "filloutId": null,
                                    "subroles": []
                                },
                                {
                                    "role": "Early Workplace Experience",
                                    "filloutId": null,
                                    "subroles": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "role": "Stage 34: Adult (22-34 years)",
                    "filloutId": null,
                    "subroles": [
                        {
                            "role": "Career Development",
                            "filloutId": null,
                            "subroles": [
                                {
                                    "role": "Workplace (Company / Startup)",
                                    "filloutId": null,
                                    "subroles": [
                                        {
                                            "role": "In-House Training Courses",
                                            "filloutId": null,
                                            "subroles": []
                                        },
                                        {
                                            "role": "Job Roles & Promotions",
                                            "filloutId": null,
                                            "subroles": []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "role": "Personal Milestones",
                            "filloutId": null,
                            "subroles": [
                                {
                                    "role": "Mortgage & Bank Loans",
                                    "filloutId": null,
                                    "subroles": []
                                },
                                {
                                    "role": "Marriage / Partnership",
                                    "filloutId": null,
                                    "subroles": []
                                }
                            ]
                        },
                        {
                            "role": "University / Continuing Education",
                            "filloutId": null,
                            "subroles": [
                                {
                                    "role": "Masters or Specialized Courses",
                                    "filloutId": null,
                                    "subroles": []
                                },
                                {
                                    "role": "Undergraduate Studies",
                                    "filloutId": null,
                                    "subroles": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "role": "Stage 89: Elderly (55+ years)",
                    "filloutId": null,
                    "subroles": [
                        {
                            "role": "Retirement Planning",
                            "filloutId": null,
                            "subroles": [
                                {
                                    "role": "Elder Care Insurance / Banking",
                                    "filloutId": null,
                                    "subroles": []
                                },
                                {
                                    "role": "Retirement Accounts / Pensions",
                                    "filloutId": null,
                                    "subroles": []
                                }
                            ]
                        },
                        {
                            "role": "Health & Leisure",
                            "filloutId": null,
                            "subroles": [
                                {
                                    "role": "Grandparent Role / Family Activities",
                                    "filloutId": null,
                                    "subroles": []
                                },
                                {
                                    "role": "Senior Community Courses",
                                    "filloutId": null,
                                    "subroles": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "role": "Stage 13: Early Teen (13-15 years)",
                    "filloutId": null,
                    "subroles": [
                        {
                            "role": "Lower Secondary School",
                            "filloutId": null,
                            "subroles": [
                                {
                                    "role": "Grade 7",
                                    "filloutId": null,
                                    "subroles": []
                                },
                                {
                                    "role": "Grade 8",
                                    "filloutId": null,
                                    "subroles": []
                                }
                            ]
                        },
                        {
                            "role": "Extracurricular Clubs",
                            "filloutId": null,
                            "subroles": []
                        }
                    ]
                },
                {
                    "role": "Stage 1: Infancy (0-1 year)",
                    "filloutId": "pnFVN8tU1mus",
                    "subroles": [
                        {
                            "role": "Stage 1: Toddler (1-3 years)",
                            "filloutId": null,
                            "subroles": [
                                {
                                    "role": "Stage 2: Early Childhood (3-5 years)",
                                    "filloutId": null,
                                    "subroles": [
                                        {
                                            "role": "Stage 3: Preschool (5-6 years)",
                                            "filloutId": null,
                                            "subroles": [
                                                {
                                                    "role": "Playgroup Activities",
                                                    "filloutId": null,
                                                    "subroles": []
                                                },
                                                {
                                                    "role": "Pre-Kindergarten",
                                                    "filloutId": null,
                                                    "subroles": []
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "role": "Stage 8: Age ~8-12 (Middle Primary)",
                    "filloutId": null,
                    "subroles": [
                        {
                            "role": "Grades 3-4",
                            "filloutId": null,
                            "subroles": [
                                {
                                    "role": "Basic Science",
                                    "filloutId": null,
                                    "subroles": []
                                },
                                {
                                    "role": "Reading Comprehension",
                                    "filloutId": null,
                                    "subroles": []
                                }
                            ]
                        },
                        {
                            "role": "Grades 5-6",
                            "filloutId": null,
                            "subroles": [
                                {
                                    "role": "Social Studies",
                                    "filloutId": null,
                                    "subroles": []
                                },
                                {
                                    "role": "Intro to Geography",
                                    "filloutId": null,
                                    "subroles": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "role": "Stage 5: Age ~5-7 (Kindergarten & Early Primary)",
                    "filloutId": null,
                    "subroles": [
                        {
                            "role": "Kindergarten",
                            "filloutId": null,
                            "subroles": [
                                {
                                    "role": "Class K2",
                                    "filloutId": null,
                                    "subroles": []
                                },
                                {
                                    "role": "Class K1",
                                    "filloutId": null,
                                    "subroles": []
                                }
                            ]
                        },
                        {
                            "role": "Primary School Basics (up to Grade 2)",
                            "filloutId": null,
                            "subroles": [
                                {
                                    "role": "Reading & Alphabet",
                                    "filloutId": null,
                                    "subroles": []
                                },
                                {
                                    "role": "Math Foundations",
                                    "filloutId": null,
                                    "subroles": []
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "role": "Second",
            "filloutId": null,
            "subroles": []
        }
    ]
})
</script>

<style scoped>
.role-test-container {
  padding: 20px;
  width: 100%;
}

.editor-container {
  margin-top: 20px;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 16px;
  background-color: #f9f9f9;
  overflow: auto;
}
</style>
