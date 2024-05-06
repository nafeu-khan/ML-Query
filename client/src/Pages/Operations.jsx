import { UploadOutlined } from "@ant-design/icons";
import { Button, Radio } from "antd";
import TextArea from "antd/es/input/TextArea";
import Upload from "antd/es/upload/Upload";
import React, { useState } from "react";
import toast, { Toaster } from "react-hot-toast";
import { BiText } from "react-icons/bi";
import { FaRegFileAudio } from "react-icons/fa6";
import AudioInput from "../Components/AudioInput";
import ShowLog from "../Components/ShowLog";

/*
CREATE ESTIMATOR salaryPredictor TYPE LR FORMULA $salary~years$;
CREATE TRAINING PROFILE oneshotSalary WITH [SELECT * FROM salary];
USE 'data/salarydb.db';
TRAIN salaryPredictor WITH TRAINING PROFILE oneshotSalary;
PREDICT WITH TRAINING PROFILE oneshotSalary BY ESTIMATOR salaryPredictor;
*/

function Operations() {
  const [type, setType] = useState("text");
  const [audioTranscript, setAudioTranscript] = useState("");
  const [query, setQuery] = useState("");
  const [rowData, setRowData] = useState();
  const [fileList, setFileList] = useState([]);
  const [data, setData] = useState([]);
  const [showTestFile, setTestFile] = useState(false);
  const [testFileList, setTestFileList] = useState([]);

  const handleExecute = async () => {
    setRowData();

    if (!query) {
      toast.error("Query can't be empty");
      return;
    }
    let inputs = query.trim();
    if (inputs[inputs.length - 1] !== ";") {
      toast.error("Invalid Query.");
      return;
    }
    inputs = inputs.split(";");
    inputs = inputs.slice(0, inputs.length - 1);
    inputs = inputs.map((val) => val.trim() + ";");
    for (let input of inputs) {
      if (!input) {
        toast.error("Invalid Query.");
        return;
      }
    }
    try {
      const formData = new FormData();
      formData.append("input", inputs);
      if (fileList && fileList[0] && fileList[0].originFileObj)
        formData.append("file", fileList[0].originFileObj);
      if (testFileList && testFileList[0] && testFileList[0].originFileObj)
        formData.append("test", testFileList[0].originFileObj);

      const res = await fetch("http://localhost:8000/test_url/", {
        method: "POST",
        body: formData,
      });
      let d = await res.json();
      d = d.replaceAll("NaN", "null");

      console.log(d);
      d = JSON.parse(d);
      
      setData((prev) => [...prev, d]);
      // setQuery("");
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div
      className={`mt-10 max-w-6xl mx-auto`}
    >
      <Toaster />
      <div className="text-center">
        {/* <Radio.Group
          size="large"
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="font-semibold"
          buttonStyle="solid"
        >
          <Radio.Button value={"text"} className=" !font-secondary">
            <div className="flex items-center gap-2">
              <span className="">Use Text</span>{" "}
              <span>
                <BiText size={22} />
              </span>
            </div>
          </Radio.Button>
          <Radio.Button value={"audio"} className=" !font-secondary">
            <div className="flex items-center gap-2">
              <span>Use Audio</span>{" "}
              <span>
                <FaRegFileAudio size={22} />
              </span>
            </div>
          </Radio.Button>
        </Radio.Group> */}
      </div>
      {/* {type === "audio" && (
        <AudioInput
          audioTranscript={audioTranscript}
          setAudioTranscript={setAudioTranscript}
        />
      )} */}
      <div className={`grid grid-cols-2 gap-4 w-full`}>
        <div className="mt-2 flex flex-col  bg-white z-50 py-4 ">
          <h1 className="text-left font-secondary text-2xl font-semibold mb-4 ">
            Enter your query:
          </h1>
          <TextArea
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              let q = e.target.value.toLowerCase().includes(" over ");
              setTestFile(q);
            }}
            rows={5}
            placeholder="Enter your SQL query"
            className="font-secondary text-gray-800 text-lg"
          />
          <div className="mt-4">
            <Upload
              className="!text-2xl"
              fileList={fileList.map((file) => ({
                ...file,
                status: "done",
              }))}
              beforeUpload={(file) => {
                setFileList([
                  { uid: file.uid, name: file.name, status: "done" },
                ]);
                return false;
              }}
              onChange={(e) => setFileList(e.fileList)}
            >
              {fileList.length === 0 && (
                <Button icon={<UploadOutlined />}>Upload File</Button>
              )}
            </Upload>
          </div>
          {showTestFile && (
            <div className="mt-4">
              <Upload
                className="!text-2xl"
                fileList={testFileList.map((file) => ({
                  ...file,
                  status: "done",
                }))}
                beforeUpload={(file) => {
                  setTestFileList([
                    { uid: file.uid, name: file.name, status: "done" },
                  ]);
                  return false;
                }}
                onChange={(e) => setTestFileList(e.fileList)}
              >
                {testFileList.length === 0 && (
                  <Button icon={<UploadOutlined />}>Upload Test File</Button>
                )}
              </Upload>
            </div>
          )}
          <button
            className="mt-4 w-28 ml-auto text-xl bg-blue-500 rounded text-white p-2 px-4 font-secondary font-semibold"
            onClick={handleExecute}
          >
            Execute
          </button>
        </div>
        
          <div className="relative top-8 resize-both overflow-auto" >
            <ShowLog data={data} setData={setData} />
          </div>
      </div>
    </div>
  );
}

export default Operations;

