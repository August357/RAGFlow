import request from "./request";

export const getFiles = () => {
  return request.get("/files");
};

export const uploadFile = (formData) => {
  return request.post(
    "/upload",
    formData,
    {
      headers:{
        "Content-Type":
        "multipart/form-data"
      }
    }
  );
};

export const deleteFile = (filename) => {
  return request.delete(
    `/file/${filename}`
  );
};

export const previewFile = (filename) => {
  return request.get(
    `/preview/${filename}`
  );
};

export const getConfig = () => {
  return request.get("/config");
};

export const buildDb = (data) => {
  return request.post(
    "/build-db",
    data
  );
};

export const getChunks = (source) => {
  return request.get("/chunks", {
    params: source ? { source } : {}
  });
};

export const getBuildStatus = () => {
  return request.get("/build-status");
};