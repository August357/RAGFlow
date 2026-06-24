import request from "./request";

// RAG问答
export const askQuestion = (query) => {
  return request.post("/ask", {
    query
  });
};