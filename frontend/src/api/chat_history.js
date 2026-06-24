import request from "./request";

export const saveChat = (data) => {
  return request.post("/chat/save", data);
};

export const getChatHistory = () => {
  return request.get("/chat/history");
};