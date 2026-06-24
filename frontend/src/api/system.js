import request from "./request";

export const getSystemInfo = () => {
  return request.get("/system");
};

export const getDashboard = () => {
  return request.get("/dashboard");
};

export const getDashboardDetail = () => {
  return request.get("/dashboard-detail");
};