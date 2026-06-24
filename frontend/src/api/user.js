import request from "./request";

export const loginApi = (data) => {

  return request.post(
    "/login",
    data
  );
};

export const registerApi = (data) => {

  return request.post(
    "/register",
    data
  );
};