import { useEffect, useState, useRef } from 'react';
import { Space, Image, Card, Badge, Row, Col, Button, notification, Pagination, Divider } from 'antd';
import Cookies from 'universal-cookie';
import { CloudDownloadOutlined, LinkOutlined } from '@ant-design/icons';
import { useParams } from "react-router-dom";

const { Meta } = Card;
interface IPixivImagesViewProps {
    apiUrl: string
}

interface IGalleryGet {
    DIRECTORYNAME: string,
    IMAGE_NUM: number,
    FILENAME: string,
    WIDTH: number,
    HEIGHT: number,
    LINKED_ARTIST_ID: number
}

const cookies = new Cookies();

const PixivImagesView = (props: IPixivImagesViewProps) => {
    const [imgData, setImgData] = useState<IGalleryGet[]>([])
    const [imgSize, setImgSize] = useState<number>(200)
    const [pageNum, setPageNum] = useState<number>(1)

    let params = useParams();

    const loadImages = async (page_num: number) => {
        const response = await fetch(`${props.apiUrl}/api/pixiv/gallery/images/${params.galleryid}?p=${page_num}`);
        const galleries = await response.json();
        setImgData(galleries)
    }

    useEffect(() => {

        loadImages(pageNum - 1)

        const cookImgSize = cookies.get("imgSize")
        if (typeof cookImgSize === "string") {
            const cookImgNumSize = Number(cookImgSize)
            if (cookImgNumSize >= 100 && cookImgNumSize <= 500)
                setImgSize(cookImgNumSize)

        }

    }, []);



    const generateGalleryCard = (gallData: IGalleryGet) => {
        return (
            <Card
                style={{ width: imgSize, height: imgSize + 100 }}
                cover={
                    generateCardImage(gallData)
                }
            >
                <Meta style={{ position: "relative", bottom: 0, left: 0, margin: "10px" }}
                    title={`${gallData.FILENAME}`}
                    description={`IMAGE_NUM: ${gallData.IMAGE_NUM}`}
                />
            </Card>
        )
    }

    const generateCardImage = (gallData: IGalleryGet) => {
        const limiting_factor = Math.max(gallData.HEIGHT, gallData.WIDTH);
        const resize_scale = limiting_factor / imgSize;
        const resized_width = Math.floor(gallData.WIDTH / resize_scale)
        const resized_height = Math.floor(gallData.HEIGHT / resize_scale)
        const leftover_width = Math.floor((imgSize - resized_width) / 2)
        return (
            <div style={{ height: resized_height, width: resized_width, left: leftover_width, position: "relative" }}>
                <Image
                    src={`${props.apiUrl}/${gallData.DIRECTORYNAME}/${gallData.FILENAME}.webp`}
                />
            </div>


        )
    }
    const onPageChange = (page_num: number, page_size: number) => {
        setPageNum(page_num)
        loadImages(page_num - 1)
    }

    return (
        <>
            <Row>
                <Col span={24}>
                    <Space size={[8, 16]} wrap>
                        {imgData.map((galldata) => generateGalleryCard(galldata))}
                        {imgData.length == 0 ? "Nothing Here...." : ""}
                    </Space>
                </Col>
            </Row>
            <Divider/>
            <Row>
                <Col>
                    <Pagination onChange={onPageChange} current={pageNum} total={50} />
                </Col>
            </Row>
        </>
    )


}


export default PixivImagesView;