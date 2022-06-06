import React, { useEffect, useState } from 'react';
import { Row, Col, Slider, Card, Divider, Space, Statistic } from 'antd';
import Cookies from 'universal-cookie';


import { ExpandOutlined } from '@ant-design/icons';


const cookies = new Cookies();



const ImageSpaceControls = () => {

    const [imgSize, setImgSize] = useState<number>(200)

    useEffect(() => {
        const cookImgSize = cookies.get("imgSize")
        if (typeof cookImgSize === "string") {
            const cookImgNumSize = Number(cookImgSize)
            if (cookImgNumSize >= 100 && cookImgNumSize <= 500)
                setImgSize(cookImgNumSize)
        }
    }, [])
    const onImgSizeSliderChange = (val: number) => {
        setImgSize(val)
        cookies.set("imgSize", imgSize)
    }

    return (
        <>
            <Row>
                <Col span={8}>
                    <Slider value={imgSize} max={500} min={100} onChange={onImgSizeSliderChange} />
                    <Card bodyStyle={{ padding: "0px" }} style={{ width: imgSize, height: imgSize + 100 }}>
                        <Space style={{ gap: "0px", backgroundColor: "darkslategray", width: "100%", height: "70px", position: "relative", top: imgSize - 5 }}>
                            <Statistic title="Card Size" value={imgSize} prefix={<ExpandOutlined />} />
                        </Space>
                    </Card>
                </Col>
            </Row>
            <Row>
                <Col span={24}>
                    <Divider />
                </Col>
            </Row>
        </>
    );
}


export default ImageSpaceControls;