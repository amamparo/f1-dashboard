import simpleRestProvider from "ra-data-simple-rest";
import { API_BASE_URL } from "./utils/common";
import { httpClient } from "./utils/api";

export const dataProvider = simpleRestProvider(API_BASE_URL, httpClient);
