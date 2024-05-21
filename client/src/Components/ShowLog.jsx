import React from "react";
import { FaAnglesRight } from "react-icons/fa6";
import AgGridTable from "../Components/AgGridTable";
import { Collapse } from "antd";

function ShowLog({ data = [], setData }) {
  return (
    <>
      <h1 className=" font-secondary flex justify-between text-2xl font-semibold ">
        <span>Output</span>
        {data.length > 0 && (
          <button
            className=" text-lg bg-blue-500 w-20 py-1 rounded text-white font-semibold"
            onClick={() => setData([])}
          >
            Clear
          </button>
        )}
      </h1>
      {data.length > 0 ? (
        <div
          className="mt-2 space-y-4 bg-gray-100 shadow-md p-3 py-5 overflow-y-auto rounded"
          style={{ maxHeight: "calc(100vh - 250px)" }}
        >
          {data.map((val, key) => {
            return (
              <Collapse
                key={key}
                className="flex items-start gap-3 !w-full"
                items={[
                  {
                    key,
                    label: (
                      <p className="font-medium text-lg">Output #{key + 1}</p>
                    ),
                    className: "w-full",
                    children: (
                      <div className="space-y-6 !w-full bg-transparent">
                        {Object.keys(val).map((v, ind) => (
                          <div key={ind}>
                            {val[v]["text"] && (
                              <p className="font-secondary text-lg text-gray-800/85 font-semibold  relative -top-2">
                                {val[v]["text"]}
                              </p>
                            )}
                            {val[v]["table"] && val[v]["table"].length > 0 && (
                              <AgGridTable rowData={val[v]["table"]} />
                            )}
                            {val[v]["graph"] && (
                              <img
                                src={`data:image/png;base64,${val[v]["graph"]}`}
                                alt=""
                              />
                            )}
                          </div>
                        ))}
                      </div>
                    ),
                  },
                ]}
              >
                {/* <p className="">
                  <FaAnglesRight size={15} />
                </p> */}
              </Collapse>
            );
          })}
        </div>
      ) : (
        <div className="bg-gray-100 shadow-md rounded mt-2 p-3 py-10 text-center font-medium text-xl">
          <p>Run a query to see the output</p>
        </div>
      )}
    </>
  );
}

export default ShowLog;
