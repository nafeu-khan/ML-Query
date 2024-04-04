import React from "react";
import { FaAnglesRight } from "react-icons/fa6";
import AgGridTable from "../Components/AgGridTable";

function ShowLog({ data = [], setData }) {
  return (
    <>
      <h1 className=" font-secondary flex justify-between text-2xl font-semibold ">
        <span>Execution Log</span>
        {data.length > 0 && (
          <button
            className=" text-lg bg-blue-500 w-20 py-1 rounded text-white font-semibold"
            onClick={() => setData([])}
          >
            Clear
          </button>
        )}
      </h1>
      <div
        className="mt-2 space-y-4 bg-gray-100 shadow-md p-3 py-5 overflow-y-auto rounded"
        style={{ maxHeight: "calc(100vh - 250px)" }}
      >
        {data.map((val, key) => {
          return (
            <div key={key} className="flex items-start gap-3">
              <p className="">
                <FaAnglesRight size={15} />
              </p>
              <div className="space-y-4">
                {Object.keys(val).map((v, ind) => (
                  <>
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
                  </>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}

export default ShowLog;
